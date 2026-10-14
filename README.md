# Pipeline de Procesamiento de Lenguaje Natural (NLP) y Análisis de Redes Semánticas

Este repositorio contiene la implementación de un *pipeline* integral de Procesamiento de Lenguaje Natural (NLP) diseñado para analizar corpus de texto no estructurado. El sistema extrae entidades, evalúa interacciones espaciales y semánticas, y modela los resultados en estructuras de grafos y matrices matemáticas.

## ⚙️ Arquitectura del Pipeline

El procesamiento se divide en módulos secuenciales para garantizar la escalabilidad y limpieza de los datos:

1. **Preprocesamiento y Estructuración (`preprocess.py`):** Limpieza de artefactos de texto (como referencias a imágenes) y segmentación automatizada de capítulos utilizando expresiones regulares (`regex`). Los datos limpios se indexan y almacenan en formato JSON.
2. **Reconocimiento de Entidades Nombradas (NER):** Integración de la librería `spaCy` (utilizando el modelo basado en Transformers `en_core_web_trf`) para extraer entidades clasificadas como `PERSON`.
3. **Normalización Algorítmica (`step2_unify.py`):** Sistema de unificación de entidades que elimina caracteres posesivos, filtra títulos irrelevantes (ej. *mr*, *sir*, *dona*) y agrupa nombres mediante lógica de evaluación de subconjuntos de *tokens*.
4. **Mapeo Espacial (`step3_positions.py`):** Extracción de las coordenadas exactas de cada entidad en el texto, registrando los índices de inicio y fin de la palabra, así como el índice de la oración a la que pertenecen.

## 🧠 Modelado de Interacciones y Análisis de Sentimiento

El núcleo analítico del proyecto evalúa cómo se relacionan las entidades extraídas:
* **Lógica de Proximidad:** Se define una conexión válida entre dos entidades si comparten la misma oración o si la distancia entre ellas es menor o igual a una ventana paramétrica (15 palabras).
* **Análisis de Polaridad:** Integración del analizador `vaderSentiment` para procesar el texto de las oraciones donde ocurren las interacciones, calculando el peso semántico compuesto (*compound score*) de cada conexión.

## 📊 Estructuras de Datos y Exportación

Los datos procesados se exportan en formatos estándar para análisis topológico y matemático:
* **Grafos de Red y Evolutivos:** Exportación de Nodos y Aristas (Edges) estáticos. Adicionalmente, el sistema segmenta la red en intervalos dinámicos predefinidos para generar grafos evolutivos que modelan los cambios topológicos a lo largo del tiempo.
* **Matrices de Coocurrencia (`step4_matrix.py`):** Construcción de matrices matemáticas simétricas (NxN) utilizando `NumPy`, donde los ejes representan el listado unificado de entidades y los valores cuantifican la frecuencia absoluta de interacción.

## 🌐 Aplicabilidad en Infraestructura y Sistemas Complejos

Aunque este *pipeline* se aplica aquí a un corpus literario, su arquitectura subyacente de análisis transversal es agnóstica al dominio. Las técnicas implementadas —parseo de texto libre[cite: 15], extracción de entidades mediante modelos Transformer[cite: 12], mapeo de proximidad de *tokens*[cite: 14] y modelado topológico matricial[cite: 11]— constituyen la base teórica necesaria para la ingesta y análisis automatizado de *logs* de servidores, detección de patrones en tráfico de red y modelado de arquitecturas distribuidas.
