import json
import pandas as pd
import numpy as np
import config


def build_matrix():
    print(f"--- STEP 4: BUILDING CO-OCCURRENCE MATRIX ---")

    # 1. LOAD POSITIONS
    print(f"Loading {config.POSITIONS_JSON}...")
    try:
        with open(config.POSITIONS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {config.POSITIONS_JSON}.")
        return

    # 2. IDENTIFY ALL UNIQUE CHARACTERS
    # We need a sorted list of all unique names to build the matrix axes
    all_names = set()
    for chapter, events in data.items():
        for event in events:
            all_names.add(event['name'])

    sorted_names = sorted(list(all_names))
    n = len(sorted_names)
    print(f"Found {n} unique characters.")

    # Map name -> index (for fast matrix access)
    name_to_idx = {name: i for i, name in enumerate(sorted_names)}

    # 3. INITIALIZE MATRIX (n x n)
    # We use numpy for speed, initialized to zeros
    matrix = np.zeros((n, n), dtype=int)

    # 4. CALCULATE MENTIONS AND CONNECTIONS
    print("Calculating connections (Window: 15 words OR Same Sentence)...")

    connection_count = 0

    for chapter, events in data.items():
        # Ensure events are sorted by position (they should be, but just in case)
        events.sort(key=lambda x: x['start'])

        num_events = len(events)

        for i in range(num_events):
            char_a = events[i]
            idx_a = name_to_idx[char_a['name']]

            # DIAGONAL: Increment total mention count for Character A
            matrix[idx_a][idx_a] += 1

            # LOOK AHEAD LOOP
            for j in range(i + 1, num_events):
                char_b = events[j]
                idx_b = name_to_idx[char_b['name']]

                # Logic 1: Same Sentence
                is_same_sentence = (char_b['sentence'] == char_a['sentence'])

                # Logic 2: Proximity (Word Distance)
                # We use 'start' of B minus 'end' of A to get the gap between them
                distance = char_b['start'] - char_a['end']

                if is_same_sentence or distance <= 15:  # Window size hardcoded as discussed
                    # VALID CONNECTION
                    # Add to both sides (Symmetry)
                    matrix[idx_a][idx_b] += 1
                    matrix[idx_b][idx_a] += 1
                    connection_count += 1
                else:
                    # OPTIMIZATION:
                    # If they are different sentences AND too far apart,
                    # we can stop checking subsequent characters in this chapter
                    # because they will only get further away.
                    # (Note: This assumes sentence indices always increase, which they do)
                    break

    print(f"Processed {connection_count} interactions.")

    # 5. SAVE TO CSV
    print("Saving Matrix...")
    df = pd.DataFrame(matrix, index=sorted_names, columns=sorted_names)
    df.to_csv(config.MATRIX_CSV)

    print("-" * 30)
    print(f"DONE! Matrix saved to: {config.MATRIX_CSV}")
    print("Action: Open the CSV in Excel to see the diagonal counts and connections.")

if __name__ == "__main__":
    build_matrix()