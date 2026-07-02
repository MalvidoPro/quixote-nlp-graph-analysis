# config.py

# --- FILE PATHS ---
# Input: The text file of the book
BOOK_FILENAME = "Files Quixote/quixote.txt"

# Output: The JSON file with the preprocessed text. The format is -> KEY(Chapter): VALUE(Text of the chapter)
PREPROCESSED_TEXT_JSON = "Files Quixote/quixote_preprocessed_text.json"

# Output: The CSV file where the name extractor saves the list of names. The format is -> | Name | Count | where the
# first column contains the name as it appears in the text and the second column contains the number of times this name
# appears
RAW_CHARACTERS_CSV = "Files Quixote/quixote_characters.csv"

# Output: The CSV file where the name unificator saves the list of clean names. The format is -> | Name | Unified Name |
# where each unique name that appears in the text has its longer and unified name associated
# (Input for the position extractor if we set the variable AUTOMATIC_EXTRACTION to True)
CLEAN_CHARACTERS_CSV = "Files Quixote/quixote_characters_clean.csv"

# Output: The CSV file where we manually verify/clean the names. The format is the same as the CLEAN_CHARACTERS_CSV
# (Input for the position extractor if we set the variable AUTOMATIC_EXTRACTIONS to False)
CHARACTERS_DICTIONARY_CSV = "Files Quixote/quixote_characters_dictionary.csv"

# Output: The JSON file where the position extractor saves the positions
POSITIONS_JSON = "Files Quixote/quixote_character_positions.json"

# Output: The JSON file who acts as a Sidecar Map of sentences so that we can use them for sentiment analysis
SENTENCES_JSON = "Files Quixote/quixote_sentences.json"

# Output: The CSV file where we save the relationships weights.
MATRIX_CSV = "Files Quixote/quixote_relationship_matrix.csv"

# --- ANALYSIS INTERVALS ---
# Format: (Start_Absolute_Chapter, End_Absolute_Chapter, "Label")
# Book 1 ends at Chapter 52. Book 2 starts at 53.
# Necessary for chapter evolution mode
CHAPTER_RANGES = [
    # --- BOOK 1 ---
    (1, 6, "01. First Sortie (B1: 1-6)"),
    (7, 14, "02. Marcela & Grisostomo (B1: 7-14)"),
    (15, 22, "03. The Yanguesans (B1: 15-22)"),
    (23, 31, "04. Sierra Morena (B1: 23-31)"),
    (32, 42, "05. Curious Impertinent (B1: 32-42)"),
    (43, 52, "06. End of Book 1 (B1: 43-52)"),

    # --- BOOK 2 (Starts at Absolute 53) ---
    (53, 62, "07. Book 2 Begins (B2: 1-10)"),
    (63, 81, "08. The Duke & Duchess (B2: 11-29)"),
    (82, 109, "09. Barataria (B2: 30-57)"),
    (110, 117, "10. Return to BCN (B2: 58-65)"),
    (118, 126, "11. The End (B2: 66-74)")
]

# Output: The CSV files where we save nodes and edges for graphic visualization.
NODES_CSV = "Files Quixote/quixote_nodes.csv"
EDGES_CSV = "Files Quixote/quixote_edges.csv"
# Output: CSV files for chapter evolution mode
NODES_EVOLUTION_CSV = "Files Quixote/quixote_nodes_evolution.csv"
EDGES_EVOLUTION_CSV = "Files Quixote/quixote_edges_evolution.csv"

# --- SETTINGS ---
# The spaCy model to use
SPACY_MODEL = "en_core_web_trf"

# How many chapters to scan? (Set to None for the whole book)
CHAPTER_LIMIT = None

# The max word distance for a connection
WINDOW_SIZE = 15

# Automatic character extraction?
AUTOMATIC_EXTRACTION = False

# The book we are working with.
# We use this variable when selecting the preprocessor.
BOOK_FORMAT = "quixote"