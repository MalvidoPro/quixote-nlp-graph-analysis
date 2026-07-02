import spacy

# First, we analise 10 sentences in spanish.

# We load spaCy NLP spanish data.
try:
    nlp_es = spacy.load("es_core_news_sm")
except IOError:
    print("Spanish model 'es_core_news_sm' not found.")
    print("Please run: python -m spacy download es_core_news_sm")
    exit()

# 10 spanish sentences
sentence_1 = "La inteligencia artificial está transformando el procesamiento del lenguaje natural."
sentence_2 = "El rápido zorro marrón salta sobre el perro perezoso."
sentence_3 = "Mañana exploraremos las antiguas ruinas que se encuentran cerca de la montaña."
sentence_4 = "¿Cuál es la capital de Rumanía y qué idioma oficial hablan allí?"
sentence_5 = "Apple podría estar interesada en comprar una startup tecnológica por mil millones."
sentence_6 = "A pesar de la lluvia, el partido de fútbol del Real Madrid continuó sin interrupciones."
sentence_7 = "El análisis de sentimientos es crucial para entender la opinión del cliente."
sentence_8 = "La biblioteca NLTK es excelente para aprender, pero spaCy es mejor para producción."
sentence_9 = "¡Qué increíblemente bien funciona este nuevo modelo de lenguaje!"
sentence_10 = "El aprendizaje profundo ha permitido avances significativos en la visión por computadora."

# Array containing the sentences.
spanish_sentences = [
    sentence_1,
    sentence_2,
    sentence_3,
    sentence_4,
    sentence_5,
    sentence_6,
    sentence_7,
    sentence_8,
    sentence_9,
    sentence_10
]

for sentence in spanish_sentences:
    doc_es = nlp_es(sentence)
    # 1-4. TOKEN, POS, LEMMA & DEPENDENCY PARSING:
    print(f"\n{'TOKEN':<12} | {'POS':<6} | {'LEMMA':<12} | {'DEP':<10} | {'HEAD'}")
    print("-" * 55)
    for token in doc_es:
        print(f"{token.text:<12} | {token.pos_:<6} | {token.lemma_:<12} | {token.dep_:<10} | {token.head.text}")

    # 5. Chunking (Noun Chunks)
    print("\n5. CHUNKING (Frases Nominales):")
    for chunk in doc_es.noun_chunks:
        print(chunk.text)

    # 6. NER (Name Entity Recognition)
    print("\n6. NER:")
    for ent in doc_es.ents:
        print(f"- {ent.text} ({ent.label_})")

import spacy

# First, we analyze 10 sentences in English.

# We load spaCy NLP English data.
try:
    nlp_en = spacy.load("en_core_web_sm")
except IOError:
    print("English model 'en_core_web_sm' not found.")
    print("Please run: python -m spacy download en_core_web_sm")
    exit()

# 10 English sentences
sentence_1 = "Artificial intelligence is transforming natural language processing."
sentence_2 = "The quick brown fox jumps over the lazy dog."
sentence_3 = "Tomorrow we will explore the ancient ruins near the mountain."
sentence_4 = "What is the capital of Romania and what official language do they speak there?"
sentence_5 = "Apple might be interested in buying a tech startup for one billion dollars."
sentence_6 = "Despite the rain, the Real Madrid football match continued without interruptions."
sentence_7 = "Sentiment analysis is crucial for understanding customer opinion."
sentence_8 = "The NLTK library is great for learning, but spaCy is better for production."
sentence_9 = "How incredibly well this new language model works!"
sentence_10 = "Deep learning has enabled significant advancements in computer vision."

# Array containing the sentences.
english_sentences = [
    sentence_1,
    sentence_2,
    sentence_3,
    sentence_4,
    sentence_5,
    sentence_6,
    sentence_7,
    sentence_8,
    sentence_9,
    sentence_10
]

for sentence in english_sentences:
    doc_en = nlp_en(sentence)

    print(f"\n--- PROCESSING SENTENCE: '{sentence}' ---")

    # 1-4. TOKEN, POS, LEMMA & DEPENDENCY PARSING:
    print(f"\n{'TOKEN':<12} | {'POS':<6} | {'LEMMA':<12} | {'DEP':<10} | {'HEAD'}")
    print("-" * 55)
    for token in doc_en:
        print(f"{token.text:<12} | {token.pos_:<6} | {token.lemma_:<12} | {token.dep_:<10} | {token.head.text}")

    # 5. Chunking (Noun Chunks)
    print("\n5. CHUNKING (Noun Chunks):")
    for chunk in doc_en.noun_chunks:
        print(chunk.text)

    # 6. NER (Name Entity Recognition)
    print("\n6. NER:")
    if not doc_en.ents:
        print("No entities found.")
    for ent in doc_en.ents:
        print(f"- {ent.text} ({ent.label_})")