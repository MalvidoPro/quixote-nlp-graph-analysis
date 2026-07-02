import re


def preprocess_lotr(filepath):
    print(f"Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        raw_text = f.read()

    # 1. GLOBAL CLEANUP
    # Remove the "useless" symbols entirely
    text = raw_text.replace('####-', '')

    # 2. SPLIT INTO CHAPTERS
    # Regex Explanation:
    # Chapter \d+\.  -> Matches "Chapter " followed by digits (1, 2, 10...) and a dot.
    # .*?            -> Matches the Chapter Title (e.g., "A Long-expected Party")
    # (?=...)        -> Lookahead: Keeps capturing text until it hits the NEXT "Chapter X" or end of file.

    pattern = r"(Chapter \d+\..*?)(?=\n\s*Chapter \d+\.|\Z)"

    # re.DOTALL allows '.' to match newlines, grabbing the whole body of the chapter
    chapters_found = re.findall(pattern, text, re.DOTALL)

    structured_book = {}
    print(f"Found {len(chapters_found)} chapters.")

    for raw_chapter in chapters_found:
        # Split Title (first line) from Content
        # We split by the first newline character
        parts = raw_chapter.split('\n', 1)

        if len(parts) < 2:
            continue  # Skip if something went wrong (e.g., empty chapter)

        title = parts[0].strip()
        content = parts[1]

        # 3. TEXT FLATTENING (Crucial for Window Logic)
        # Replace newlines with spaces so sentences don't break
        clean_content = content.replace('\n', ' ')

        # Remove double spaces (artifacts from replacing newlines)
        clean_content = " ".join(clean_content.split())

        structured_book[title] = clean_content

    return structured_book


# --- RUN IT ---
book_data = preprocess_lotr('lotr.txt')

# --- VERIFY THE OUTPUT ---
if len(book_data) > 0:
    first_title = list(book_data.keys())[0]
    print(f"\nExample Chapter: {first_title}")
    print(f"Character Count: {len(book_data[first_title])}")
    print(f"Preview (First 200 chars):")
    print(f"'{book_data[first_title][:200]}...'")
else:
    print("No chapters found! Check if the Regex matches your text format.")