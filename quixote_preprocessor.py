import re
import json
import config  # We need this to get the output filename


def preprocess_don_quixote():
    filepath = config.BOOK_FILENAME
    print(f"Reading {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()
    except FileNotFoundError:
        print(f"Error: Could not find file at {filepath}")
        return

    # 1. SPLIT INTO CHAPTERS
    # Looks for "CHAPTER" + Roman Numerals + "."
    pattern = r"(CHAPTER\s+[IVXLCDM]+\..*?)(?=\n\s*CHAPTER\s+[IVXLCDM]+\.|\Z)"
    chapters_found = re.findall(pattern, raw_text, re.DOTALL)

    structured_book = {}
    print(f"Found {len(chapters_found)} chapters.")

    for i, raw_chapter in enumerate(chapters_found):
        # Separate Header from Content
        parts = raw_chapter.split('\n', 1)
        if len(parts) < 2:
            continue

        header = parts[0].strip()
        content = parts[1]

        # --- REMOVE IMAGE ARTIFACTS ---
        content = re.sub(r'\S+\.jpg\s*\(\d+K\)', '', content)
        content = re.sub(r'Full Size', '', content)

        # 3. TEXT FLATTENING
        clean_content = content.replace('\n', ' ')
        clean_content = " ".join(clean_content.split())

        # Create unique key
        unique_key = f"{i + 1:03d}_{header}"
        structured_book[unique_key] = clean_content

    # --- SAVE TO JSON (The "Storage" Step) ---
    output_file = config.PREPROCESSED_TEXT_JSON

    print(f"Saving cleaned text to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(structured_book, f, indent=4)

    print("DONE! Data storaged successfully.")


# --- EXECUTION ---
if __name__ == "__main__":
    # Ensure this matches your actual text file location
    preprocess_don_quixote()