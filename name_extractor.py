import spacy
import pandas as pd
from collections import Counter
import config

def extract_names(book_data, nlp):
    print(f"--- STEP 1: EXTRACTING NAMES FROM {config.BOOK_FILENAME} ---")

    all_names = []

    print("Scanning chapters...")
    for i, (title, text) in enumerate(book_data.items()):

        if config.CHAPTER_LIMIT and i >= config.CHAPTER_LIMIT:
            print(f"  Reached limit of {config.CHAPTER_LIMIT} chapters. Stopping.")
            break

        doc = nlp(text)

        for ent in doc.ents:
            if ent.label_ == "PERSON":
                name = ent.text.strip().replace('\n', ' ')

                if len(name) > 2:
                    all_names.append(name)

        if (i + 1) % 5 == 0:
            print(f"  Processed {i + 1} chapters...")

    # 4. Save to CSV
    print("Counting frequencies...")
    counts = Counter(all_names)
    df = pd.DataFrame(counts.items(), columns=['Name', 'Count'])
    df = df.sort_values(by='Count', ascending=False)

    df.to_csv(config.RAW_CHARACTERS_CSV, index=False)

    print("-" * 30)
    print(f"DONE! Found {len(df)} unique names.")
    print(f"File saved to: {config.RAW_CHARACTERS_CSV}")