# Automated Extraction of Character Interaction Networks — Don Quixote

Proyecto de Procesamiento de Lenguaje Natural (NLP) y teoría de grafos diseñado para extraer, analizar y visualizar de forma automatizada la **Red de Interacción de Personajes** (*Character Interaction Network*) de **Don Quijote de la Mancha** (*Don Quixote*, de Miguel de Cervantes), aplicando técnicas de *distant reading* sobre el texto íntegro en inglés procedente de Project Gutenberg ($\approx 400\,000$ palabras distribuidas en $126$ capítulos).

El sistema transforma texto literario no estructurado en un grafo ponderado $G = (V, E)$, donde los nodos $V$ representan a los personajes (dimensionados según su frecuencia de aparición), las aristas $E$ reflejan la fuerza de su interacción mediante una regla híbrida de coocurrencia, y el color de cada enlace representa la polaridad emocional (amistad frente a animadversión) calculada con **VADER**.

---

## 📋 Tabla de Contenidos

1. [Planteamiento del Problema y Fundamento Teórico](#-planteamiento-del-problema-y-fundamento-teórico)
2. [Arquitectura Modular (Pipeline Final)](#-arquitectura-modular-pipeline-final)
3. [Iteraciones de Diseño y Scripts Alternativos Descartados](#-iteraciones-de-diseño-y-scripts-alternativos-descartados)
4. [Estructura del Repositorio](#-estructura-del-repositorio)
5. [Requisitos e Instalación](#-requisitos-e-instalación)
6. [Pasos para Ejecutar el Programa](#-pasos-para-ejecutar-el-programa)
7. [Visualización de Resultados en Gephi](#-visualización-de-resultados-en-gephi)
8. [Trabajo Futuro y Mejoras](#-trabajo-futuro-y-mejoras)
9. [Autor](#-autor)

---

## 🧠 Planteamiento del Problema y Fundamento Teórico

Analizar la red social subyacente de una novela extensa mediante lectura tradicional resulta complejo. Este proyecto implementa un pipeline secuencial **ETL (Extract, Transform, Load)** dividido en tres pilares teóricos:

### 1. Reconocimiento de Entidades Nombradas (NER) y Unificación de Nombres
- **Modelo Transformer (`en_core_web_trf`)**: Se emplea la librería **spaCy** con una arquitectura preentrenada basada en **RoBERTa**. A diferencia de los modelos estadísticos clásicos (HMM, CRF) o de los modelos ligeros basados en CNN (`en_core_web_sm`), el modelo transformer captura información contextual profunda para distinguir con mayor precisión nombres de personajes (`PERSON`) frente a lugares o conceptos abstractos:

$$E(w_{1\dots n}) \rightarrow \{(w_i, \dots, w_j) : \text{LABEL}\}$$

- **Algoritmo de Unificación**: La salida bruta del NER suele estar fragmentada, tratando variantes como *"Quixote"*, *"Don Quixote"*, *"Sancho"* o *"Señor Panza"* como entidades distintas. El algoritmo normaliza las cadenas (conversión a minúsculas, eliminación de posesivos `'s` / `’s` y filtrado de títulos como `mr`, `mrs`, `miss`, `dr`, `don`, `dona`, `lady`, `sir`, `the`, `señor`) y agrupa las variantes bajo un único nodo canónico mediante **coincidencia de subcadenas** (*Substring match*) y **subconjuntos de tokens** (*Token Subset match*).
- **Diccionario Curado (*Golden Rule*) frente a Extracción Automática**: Dado que el NER de spaCy aún puede clasificar erróneamente ciertos lugares o conceptos como personas (por ejemplo, *La Mancha* o *God*) y que aplicar un umbral estricto de apariciones (`Count >= 5`) descarta personajes secundarios relevantes, en la versión final para *El Quijote* se optó por elaborar un diccionario de personajes curado y verificado (`Files Quixote/quixote_characters_dictionary.csv`) con apoyo de IA (`AUTOMATIC_EXTRACTION = False`). No obstante, los módulos de extracción y unificación automática (`name_extractor.py` y `name_unificator.py`) se conservan íntegros en la arquitectura (`AUTOMATIC_EXTRACTION = True`) para garantizar la **escalabilidad** del sistema a cualquier otra novela menos conocida.

### 2. Extracción de Relaciones (Regla de Coocurrencia Híbrida)
Para aproximar qué constituye una interacción narrativa entre dos personajes distintos $A$ y $B$ (evitando bucles propios donde $A = B$), se define una **Regla de Coocurrencia Híbrida**:
1. **Proximidad Sintáctica**: Ambos personajes aparecen en la **misma oración** (`char_b['sentence'] == char_a['sentence']`), lo que suele indicar diálogo directo o acción compartida.
2. **Proximidad Espacial**: Ambos personajes aparecen dentro de una **ventana deslizante de $15$ palabras** (`char_b['start'] - char_a['end'] <= 15`), capturando interacciones que cruzan el límite entre dos oraciones consecutivas (por ejemplo: *"Don Quixote asked. Sancho replied."*).

El peso total $W_{AB}$ de la arista entre $A$ y $B$ se define como la suma de todas sus coocurrencias a lo largo de la novela:

$$W_{AB} = \sum_{i=1}^{N} \mathbb{I}(\text{Co-occurrence}_i(A, B))$$

### 3. Análisis de Sentimiento (VADER) y Estrategia *Sidecar*
- **Evaluación con VADER**: Para dotar a la red de una dimensión emocional, cada vez que se detecta una interacción entre $A$ y $B$ se analiza la oración correspondiente mediante **VADER** (*Valence Aware Dictionary and sEntiment Reasoner*). La puntuación final de sentimiento de la arista $S_{AB} \in [-1, 1]$ corresponde al promedio del índice `compound` de todos los contextos de interacción:

$$S_{AB} = \frac{\sum_{i=1}^{N} \text{VADER}(\text{Context}_i)}{N}$$

- **Estrategia *Sidecar***: Releer y segmentar todo el libro cada vez que se calcula el sentimiento sería computacionalmente costoso. Para optimizarlo, durante el Paso 3 (`position_extractor.py`) el sistema construye y guarda simultáneamente un mapa independiente con todas las oraciones indexadas por capítulo (`Files Quixote/quixote_sentences.json`). Así, el constructor del grafo (`graph_builder.py`) accede instantáneamente al texto exacto de cualquier oración mediante su índice.

---

## ⚙️ Arquitectura Modular (Pipeline Final)

El proyecto final consta de **5 módulos principales** apoyados por el archivo de configuración `config.py`, utilizando archivos JSON y CSV como almacenamiento intermedio para no tener que reejecutar el modelo de spaCy al ajustar parámetros del grafo:

| Módulo | Script | Estado en el Flujo Final | Descripción |
| :--- | :--- | :--- | :--- |
| **Configuración** | `config.py` | **Activo** | Centraliza todas las rutas de entrada/salida, el modelo `en_core_web_trf`, el límite de capítulos (`CHAPTER_LIMIT`), el tamaño de ventana (`WINDOW_SIZE = 15`), los rangos de capítulos y el selector `AUTOMATIC_EXTRACTION`. |
| **1. Preprocesador** | `quixote_preprocessor.py` | **Activo (Paso 0)** | Lee `Files Quixote/quixote.txt`, divide el texto en $126$ capítulos mediante expresiones regulares (`CHAPTER\s+[IVXLCDM]+\.`), limpia referencias a imágenes (`.jpg`, `Full Size`), aplana saltos de línea y exporta `quixote_preprocessed_text.json`. |
| **2. Extractor de Nombres** | `name_extractor.py` | *Opcional* (`AUTOMATIC_EXTRACTION = True`) | Ejecuta el modelo NER (`en_core_web_trf`) capítulo a capítulo para extraer todas las entidades con etiqueta `PERSON` (longitud $> 2$) y guarda sus frecuencias en `quixote_characters.csv`. |
| **3. Unificador de Nombres** | `name_unificator.py` | *Opcional* (`AUTOMATIC_EXTRACTION = True`) | Normaliza los nombres en bruto, filtra aquellos con al menos $5$ apariciones (`Count >= 5`), elimina títulos honoríficos y agrupa variantes en `quixote_characters_clean.csv`. |
| **4. Extractor de Posiciones y Oraciones** | `position_extractor.py` | **Activo (Paso 3)** | Carga el diccionario de personajes (`quixote_characters_dictionary.csv` por defecto, o `quixote_characters_clean.csv` si `AUTOMATIC_EXTRACTION = True`), localiza las coordenadas exactas de cada mención (`start`, `end`, `sentence`) en `quixote_character_positions.json` y genera el mapa *sidecar* de oraciones en `quixote_sentences.json`. |
| **5. Constructor del Grafo** | `graph_builder.py` | **Activo (Paso 4)** | Cruza las coordenadas de personajes con el mapa *sidecar* de oraciones, evalúa la coocurrencia híbrida (misma oración o distancia $\le 15$ palabras), calcula la polaridad promedio con VADER y exporta `quixote_nodes.csv` y `quixote_edges.csv` listos para Gephi. |

---

## 🔄 Iteraciones de Diseño y Scripts Alternativos Descartados

Durante el desarrollo del proyecto se exploraron enfoques alternativos cuyos scripts se mantienen en el repositorio con fines documentales, aunque **no son necesarios en la ejecución final**:

1. **Alternativa 1 — Constructor de Matriz de Adyacencia (`matrix_builder.py`)**:
   - *Funcionamiento*: Construía con **NumPy** una matriz simétrica $n \times n$ (`Files Quixote/quixote_relationship_matrix.csv`) donde la celda $(A, B)$ almacenaba el peso de la interacción entre $A$ y $B$, y la diagonal principal $(A, A)$ registraba el número total de apariciones del personaje $A$ en la novela.
   - *Motivo de descarte*: Aunque matemáticamente elegante y compacta, resultó inadecuada para la visualización en Gephi, ya que esta herramienta requiere tablas separadas de **Nodos** y **Aristas** para poder asignar metadatos como el color de sentimiento de cada enlace o el peso individual de los nodos. Fue reemplazada por `graph_builder.py`.

2. **Alternativa 2 — Grafo Evolutivo por Intervalos (`graph_builder_intervals.py`)**:
   - *Funcionamiento*: Etiquetaba cada nodo y cada interacción con uno de los $11$ intervalos de capítulos definidos en `config.CHAPTER_RANGES` ($6$ bloques para la Primera Parte y $5$ para la Segunda Parte), exportando `quixote_nodes_evolution.csv` y `quixote_edges_evolution.csv` para crear una animación dinámica en Gephi mediante filtros de partición.
   - *Motivo de descarte*: Debido a la complejidad de gestionar filtros temporales (*time-slices*) y a la inestabilidad espacial de los nodos entre intervalos en Gephi, los resultados dinámicos eran inconsistentes. Se optó finalmente por generar instantáneas estáticas de alta calidad (red global, primeros $10$ capítulos y últimos $10$ capítulos) mediante `graph_builder.py`.

---

## 📂 Estructura del Repositorio

```text
quixote-nlp-graph-analysis/
├── config.py                                # Configuración global, rutas de archivos y parámetros
├── quixote_preprocessor.py                  # Módulo 1 (Paso 0): Limpieza Regex y división en 126 capítulos
├── name_extractor.py                        # Módulo 2 (Paso 1 - Opcional): Extracción NER de entidades PERSON
├── name_unificator.py                       # Módulo 3 (Paso 2 - Opcional): Unificación automática de nombres
├── position_extractor.py                    # Módulo 4 (Paso 3): Coordenadas de personajes y mapa Sidecar de oraciones
├── graph_builder.py                         # Módulo 5 (Paso 4): Construcción del grafo final y sentimiento VADER
├── matrix_builder.py                        # [Descartado - Alternativa 1] Matriz de adyacencia simétrica n x n
├── graph_builder_intervals.py               # [Descartado - Alternativa 2] Grafo evolutivo por intervalos de capítulos
├── requirements.txt                         # Dependencias externas de Python
├── README.md                                # Documentación del repositorio
└── Files Quixote/
    ├── quixote.txt                          # Texto íntegro de Don Quixote (Project Gutenberg)
    ├── quixote_preprocessed_text.json       # Texto limpio dividido en 126 capítulos (Salida Paso 0)
    ├── quixote_characters.csv               # Conteo bruto de entidades PERSON (Salida Paso 1)
    ├── quixote_characters_clean.csv         # Diccionario unificado automáticamente (Salida Paso 2)
    ├── quixote_characters_dictionary.csv    # Diccionario curado de personajes (Entrada por defecto al Paso 3)
    ├── quixote_character_positions.json     # Posiciones exactas e índice de oración por capítulo (Salida Paso 3)
    ├── quixote_sentences.json               # Mapa Sidecar de oraciones por capítulo (Salida Paso 3)
    ├── quixote_nodes.csv                    # Tabla final de Nodos para Gephi (Salida Paso 4)
    ├── quixote_edges.csv                    # Tabla final de Aristas con sentimiento para Gephi (Salida Paso 4)
    ├── quixote_relationship_matrix.csv      # Matriz de coocurrencia (Salida de matrix_builder.py)
    ├── quixote_nodes_evolution.csv          # Nodos por intervalo (Salida de graph_builder_intervals.py)
    └── quixote_edges_evolution.csv          # Aristas por intervalo (Salida de graph_builder_intervals.py)
```

---

## 🚀 Requisitos e Instalación

Para ejecutar el proyecto se recomienda utilizar **Python 3.11.13** (versión con la que fue desarrollado y validado).

### 1. Clonar el repositorio
```bash
git clone https://github.com/MalvidoPro/quixote-nlp-graph-analysis.git
cd quixote-nlp-graph-analysis
```

### 2. Crear y activar un entorno virtual

En **Linux / macOS**:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

En **Windows (PowerShell)**:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instalar las dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Descargar el modelo Transformer de spaCy (`en_core_web_trf`)
```bash
python -m spacy download en_core_web_trf
```

---

## ▶️ Pasos para Ejecutar el Programa

> **Nota:** La carpeta `Files Quixote/` ya incluye los archivos intermedios y finales precalculados. Puedes ejecutar únicamente las etapas que desees o regenerar todo el flujo desde cero.

### Opción A: Ejecución Estándar Recomendada (Usando el Diccionario Curado)

Por defecto, `config.py` tiene establecido `AUTOMATIC_EXTRACTION = False`, lo que utiliza directamente el diccionario verificado (`Files Quixote/quixote_characters_dictionary.csv`) y omite los Pasos 1 y 2:

1. **Paso 0 — Preprocesar la novela y dividirla en capítulos:**
   ```bash
   python quixote_preprocessor.py
   ```
   *Genera `Files Quixote/quixote_preprocessed_text.json`.*

2. **Paso 3 — Localizar personajes y generar el mapa *Sidecar* de oraciones:**
   ```bash
   python position_extractor.py
   ```
   *Genera `Files Quixote/quixote_character_positions.json` y `Files Quixote/quixote_sentences.json`.*  
   *(Consejo: Analizar los $126$ capítulos con `en_core_web_trf` requiere un tiempo de cómputo elevado. Si deseas realizar una prueba rápida o generar el grafo de los primeros capítulos, puedes ajustar `CHAPTER_LIMIT = 10` en `config.py`).*

3. **Paso 4 — Construir el grafo de interacciones y calcular el sentimiento con VADER:**
   ```bash
   python graph_builder.py
   ```
   *Genera `Files Quixote/quixote_nodes.csv` y `Files Quixote/quixote_edges.csv`.*

---

### Opción B: Ejecución con Extracción Automática Completa (Incluyendo Pasos 1 y 2)

Si deseas ejecutar todo el pipeline de descubrimiento automático de personajes desde cero (o adaptarlo a otra obra literaria):

1. Abre `config.py` y cambia `AUTOMATIC_EXTRACTION = True`.
2. **Paso 0 — Preprocesar el texto:**
   ```bash
   python quixote_preprocessor.py
   ```
3. **Paso 1 — Extraer nombres en bruto con el NER de spaCy:**  
   Dado que `name_extractor.py` define la función `extract_names(book_data, nlp)`, puedes invocarla directamente desde la terminal:
   ```bash
   python -c "import json, spacy, config, name_extractor; book = json.load(open(config.PREPROCESSED_TEXT_JSON, encoding='utf-8')); nlp = spacy.load(config.SPACY_MODEL); name_extractor.extract_names(book, nlp)"
   ```
   *Genera `Files Quixote/quixote_characters.csv`.*
4. **Paso 2 — Limpiar y unificar variantes de nombres:**
   ```bash
   python name_unificator.py
   ```
   *Genera `Files Quixote/quixote_characters_clean.csv`.*
5. **Pasos 3 y 4 — Extraer posiciones y construir el grafo final:**
   ```bash
   python position_extractor.py
   python graph_builder.py
   ```

---

### Opción C: Ejecutar los Scripts Alternativos (Opcional)

Si deseas reproducir los archivos de las dos alternativas descartadas durante la fase de diseño (requiere haber ejecutado previamente hasta el Paso 3):

```bash
# Alternativa 1: Generar la matriz simétrica de coocurrencia (quixote_relationship_matrix.csv)
python matrix_builder.py

# Alternativa 2: Generar nodos y aristas por intervalos de capítulos (quixote_nodes_evolution.csv y quixote_edges_evolution.csv)
python graph_builder_intervals.py
```

---

## 📊 Visualización de Resultados en Gephi

Para visualizar la red generada por `graph_builder.py`:

1. Abre **Gephi** y crea un **Nuevo Proyecto**.
2. En **Laboratorio de Datos** (*Data Laboratory*) $\rightarrow$ **Importar hoja de cálculo** (*Import Spreadsheet*):
   - Importa primero `Files Quixote/quixote_nodes.csv` como **Tabla de nodos** (`Id`, `Label`, `Weight`).
   - Importa a continuación `Files Quixote/quixote_edges.csv` como **Tabla de aristas** (`Source`, `Target`, `Weight`, `Avg_Sentiment`, `Type: Undirected`) seleccionando la opción *Añadir al espacio de trabajo existente* (*Append to existing workspace*).
3. En la pestaña **Vista General** (*Overview*):
   - **Tamaño de los Nodos (*Node Size*)**: En *Apariencia $\rightarrow$ Nodos $\rightarrow$ Tamaño $\rightarrow$ Ranking*, selecciona `Weight` (número de apariciones). *Don Quixote* y *Sancho Panza* destacarán como los nodos centrales de mayor tamaño.
   - **Grosor de las Aristas (*Edge Thickness*)**: Proporcional al atributo `Weight` de cada relación.
   - **Color por Sentimiento (*Sentiment Gradient*)**: En *Apariencia $\rightarrow$ Aristas $\rightarrow$ Color $\rightarrow$ Ranking*, selecciona `Avg_Sentiment` aplicando un gradiente desde **Rojo** (interacciones hostiles/negativas) hasta **Verde** (interacciones amistosas/positivas).
   - **Algoritmo de Distribución (*Layout*)**: Ejecuta **Force Atlas 2** para espacializar el grafo.

---

## 🔮 Trabajo Futuro y Mejoras

1. **Evolución Dinámica Capítulo a Capítulo**: Almacenar el estado de los nodos y aristas en cada capítulo individual para reproducir la secuencia temporal completa en un visualizador de grafos.
2. **Resolución de Correferencias (*Coreference Resolution*)**: Incorporar un modelo capaz de vincular pronombres (*"he"*, *"she"*, *"him"*) con sus nombres propios correspondientes, incrementando la densidad y precisión de las interacciones detectadas.
3. **Nuevas Métricas de Volatilidad Relacional**: Diseñar métricas que cuantifiquen el grado de cambio que experimenta una relación a lo largo de la novela (transiciones de amistad a enemistad o viceversa, y atenuación o fortalecimiento de la intensidad del vínculo).

---

## 👤 Autor

- **Jorge Malvido Guillén** — [@MalvidoPro](https://github.com/MalvidoPro)
