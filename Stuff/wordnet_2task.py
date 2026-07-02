import nltk
from nltk.corpus import wordnet as wn

# Descargar datos de WordNet (solo la primera vez)
try:
    wn.synsets('dog', pos='n')
except:
    print("Downloading from WordNet...")
    nltk.download('wordnet')
    nltk.download('omw-1.4')  # Open Multilingual Wordnet

# --- Define tus 8 palabras ---
# (3 sustantivos, 3 verbos, 2 adjetivos)
palabras = [
    ('dog', 'n'), ('car', 'n'), ('love', 'n'),
    ('run', 'v'), ('eat', 'v'), ('think', 'v'),
    ('happy', 'a'), ('strong', 'a')
]

# --- Escribir resultados en un archivo ---
with open('wordnet_results.txt', 'w', encoding='utf-8') as f:
    for palabra, pos in palabras:
        f.write(f"========================================\n")
        f.write(f" PALABRA: {palabra} (Tipo: {pos})\n")
        f.write(f"========================================\n\n")

        synsets = wn.synsets(palabra, pos=pos)

        if not synsets:
            f.write("No synsets found for this word.\n\n")
            continue

        for i, syn in enumerate(synsets):
            f.write(f"--- Meaning {i + 1}: {syn.name()} ---\n")

            # 1. Definición
            f.write(f"  Definition: {syn.definition()}\n")

            # 2. Literales (lemmas)
            f.write(f"  Lemmas: {[lemma.name() for lemma in syn.lemmas()]}\n")

            # 3. Relaciones Semánticas (ej. Hiperónimos y Merónimos)
            hiperonimos = syn.hypernyms()
            if hiperonimos:
                f.write(f"  Relation (Hypernyms): {[h.name() for h in hiperonimos]}\n")

            # Mostrar una relación *diferente*
            meronimos = syn.part_meronyms()
            if meronimos:
                f.write(f"  Relation (Meronyms - Parts): {[m.name() for m in meronimos]}\n")

            f.write("\n")