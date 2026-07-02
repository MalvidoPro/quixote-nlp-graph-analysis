import nltk
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize

# --- NLTK and Stemmer Setup ---

# Download the 'punkt' tokenizer if you don't have it
# (required for word_tokenize)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading NLTK 'punkt' tokenizer...")
    nltk.download('punkt')

# 1. Instantiate the stemmers as requested
stemmerESP = SnowballStemmer("spanish")
stemmerENG = SnowballStemmer("english")

# --- 2. Sentence Lists ---

# 10 Spanish sentences
spanish_sentences = [
    "La inteligencia artificial está transformando el procesamiento del lenguaje natural.",
    "El rápido zorro marrón salta sobre el perro perezoso.",
    "Mañana exploraremos las antiguas ruinas que se encuentran cerca de la montaña.",
    "¿Cuál es la capital de Rumanía y qué idioma oficial hablan allí?",
    "Apple podría estar interesada en comprar una startup tecnológica por mil millones.",
    "A pesar de la lluvia, el partido de fútbol del Real Madrid continuó sin interrupciones.",
    "El análisis de sentimientos es crucial para entender la opinión del cliente.",
    "La biblioteca NLTK es excelente para aprender, pero spaCy es mejor para producción.",
    "¡Qué increíblemente bien funciona este nuevo modelo de lenguaje!",
    "El aprendizaje profundo ha permitido avances significativos en la visión por computadora."
]

# 10 English sentences
english_sentences = [
    "Artificial intelligence is transforming natural language processing.",
    "The quick brown fox jumps over the lazy dog.",
    "Tomorrow we will explore the ancient ruins near the mountain.",
    "What is the capital of Romania and what official language do they speak there?",
    "Apple might be interested in buying a tech startup for one billion dollars.",
    "Despite the rain, the Real Madrid football match continued without interruptions.",
    "Sentiment analysis is crucial for understanding customer opinion.",
    "The NLTK library is great for learning, but spaCy is better for production.",
    "How incredibly well this new language model works!",
    "Deep learning has enabled significant advancements in computer vision."
]

# --- 3. Stemming Analysis (Spanish) ---

print("=" * 60)
print(" STEMMING ANALYSIS (SPANISH) WITH SNOWBALLSTEMMER")
print("=" * 60)

for sentence in spanish_sentences:
    print(f"\n--- SENTENCE: '{sentence}' ---")

    # Tokenize (split into words)
    tokens = word_tokenize(sentence, language='spanish')

    print(f"{'TOKEN':<18} | {'STEM'}")
    print("-" * 30)

    for token in tokens:
        # Apply stemming to each token
        stem = stemmerESP.stem(token)
        print(f"{token:<18} | {stem}")

# --- 4. Stemming Analysis (English) ---

print("\n" + "=" * 60)
print(" STEMMING ANALYSIS (ENGLISH) WITH SNOWBALLSTEMMER")
print("=" * 60)

for sentence in english_sentences:
    print(f"\n--- SENTENCE: '{sentence}' ---")

    # Tokenize (English is the default language)
    tokens = word_tokenize(sentence, language='english')

    print(f"{'TOKEN':<18} | {'STEM'}")
    print("-" * 30)

    for token in tokens:
        # Apply stemming to each token
        stem = stemmerENG.stem(token)
        print(f"{token:<18} | {stem}")


