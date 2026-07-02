import spacy
import pandas as pd
import json
import config


def load_character_map():
    """
    Loads the clean CSV into a dictionary for fast lookup.
    """
    if config.AUTOMATIC_EXTRACTION:
        input_file = config.CLEAN_CHARACTERS_CSV
    else:
        input_file = config.CHARACTERS_DICTIONARY_CSV
    print(f"Loading Character Map from {input_file}...")
    try:
        df = pd.read_csv(input_file)
        # Create a dictionary: Name -> Unified_Name
        # Ensure keys are stripped and lowercase just in case
        return dict(zip(df['Name'].str.strip().str.lower(), df['Unified_Name']))
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}.")
        return {}


def extract_positions():
    print(f"--- STEP 3: LOCATING CHARACTERS IN {config.BOOK_FILENAME} AND GETTING RELEVANT SENTENCES ---")

    # 1. LOAD THE CHARACTER MAP
    name_map = load_character_map()
    if not name_map:
        return

    final_data = {}
    sentence_map = {}
    total_mentions = 0

    # 2. LOAD MODEL
    print(f"Loading model: {config.SPACY_MODEL}...")
    nlp = spacy.load(config.SPACY_MODEL)

    # 3. LOAD CLEANED BOOK DATA (text of the book divided into chapters)
    input_file = config.PREPROCESSED_TEXT_JSON
    print(f"Loading book text from {input_file}...")

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            book_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}. Please run the preprocessor module first.")
        return

    print("Scanning chapters for verified characters...")

    # 4. SCANNING LOOP
    for i, (chapter_title, text) in enumerate(book_data.items()):
        # Check limit (defined in config.py)
        if config.CHAPTER_LIMIT and i >= config.CHAPTER_LIMIT:
            print(f"  Reached limit of {config.CHAPTER_LIMIT} chapters. Stopping.")
            break

        doc = nlp(text)

        # A. BUILD SENTENCE MAP
        # Store raw text of every sentence
        # We need to list-ify it so we can index it later
        current_sentences_text = [sent.text.strip() for sent in doc.sents]
        sentence_map[chapter_title] = current_sentences_text

        # B. LOCATE CHARACTERS
        chapter_events = []

        # We assume standard spaCy sentence boundaries
        # enumerate(doc.sents) gives us the Sentence Index (0, 1, 2...)
        for sent_idx, sent in enumerate(doc.sents):

            # Check entities inside this sentence
            for ent in sent.ents:
                if ent.label_ == "PERSON":
                    # CLEAN: Lowercase + Remove \n + Remove 's
                    raw_text = ent.text.lower().strip().replace('\n', ' ')
                    if raw_text.endswith("'s") or raw_text.endswith("’s"):
                        raw_text = raw_text[:-2]

                    # CHECK: Is this name in our Dictionary?
                    if raw_text in name_map:
                        unified_name = name_map[raw_text]

                        # RECORD: Save the position and sentence index
                        chapter_events.append({
                            "name": unified_name,
                            "start": ent.start,  # Word index in chapter
                            "end": ent.end,
                            "sentence": sent_idx  # Necessary to understand if two characters are in the same sentence
                        })

        final_data[chapter_title] = chapter_events
        count = len(chapter_events)
        total_mentions += count

        if count > 0:
            print(f"  {chapter_title[:20]}... -> {len(current_sentences_text)} sentences, {count} characters")

    # 5. SAVE JSON
    with open(config.POSITIONS_JSON, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=4)

    with open(config.SENTENCES_JSON, 'w', encoding='utf-8') as f:
        json.dump(sentence_map, f, indent=4)

    print("-" * 30)
    print(f"DONE! Found {total_mentions} verified mentions.")
    print(f"Location data saved to: {config.POSITIONS_JSON} and sentences saved to {config.SENTENCES_JSON}.")

if __name__ == "__main__":
    extract_positions()