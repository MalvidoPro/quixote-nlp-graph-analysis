import pandas as pd
import config

# Words to ignore when comparing names (Titles & Articles)
TITLES = {'mr', 'mrs', 'miss', 'dr', 'don', 'dona', 'lady', 'sir', 'the', 'señor'}


def get_significant_tokens(name_str):
    """
    Splits a name into words and removes titles.
    Input: "mr panza" -> Output: {'panza'}
    """
    tokens = set(name_str.split())
    # Return tokens that are NOT in the titles list
    return {t for t in tokens if t not in TITLES}


def clean_and_normalize(text):
    """
    Converts to lowercase and removes possessive 's.
    """
    # 1. Lowercase and strip whitespace
    text = text.lower().strip()

    # 2. Remove possessive 's at the end
    if text.endswith("’s") or text.endswith("'s"):
        text = text[:-2]

    return text


def unify_names():
    print(f"--- STEP 2: CLEANING & UNIFYING NAMES FROM {config.RAW_CHARACTERS_CSV} ---")

    # 1. LOAD RAW DATA
    try:
        df = pd.read_csv(config.RAW_CHARACTERS_CSV)
    except FileNotFoundError:
        print(f"Error: Could not find {config.RAW_CHARACTERS_CSV}.")
        return

    # 2. NORMALIZE (Lowercase + Remove 's)
    # We apply the function we defined above
    df['clean_name'] = df['Name'].apply(clean_and_normalize)

    # 3. AGGREGATE COUNTS
    grouped_df = df.groupby('clean_name')['Count'].sum().reset_index()

    # Sort by size of the name so the biggest version is the parent
    grouped_df = grouped_df.sort_values(
        by='clean_name',
        key=lambda x: x.str.len(),
        ascending=False
    )

    # 4. TAKE OUT IRRELEVANT NAMES
    grouped_df = grouped_df[grouped_df['Count'] >= 5]

    print(f"Reduced to {len(grouped_df)} unique clean names.")

    # 4. SMART UNIFICATION (Token Matching)
    final_data = []
    known_parents = []

    candidates = grouped_df.to_dict('records')

    for item in candidates:
        name = item['clean_name']

        name_tokens = get_significant_tokens(name)
        suggested_parent = name  # Default

        # Check against existing parents
        for parent in known_parents:
            parent_tokens = get_significant_tokens(parent)

            # LOGIC A: Substring match
            if name in parent and name != parent:
                suggested_parent = parent
                break

            # LOGIC B: Token Subset match
            if name_tokens and name_tokens.issubset(parent_tokens):
                suggested_parent = parent
                break

        if suggested_parent == name:
            known_parents.append(name)

        final_data.append({
            "Name": name,
            "Unified_Name": suggested_parent
        })

    # 5. SAVE
    result_df = pd.DataFrame(final_data)
    result_df = result_df[['Name', 'Unified_Name']]
    result_df.to_csv(config.CLEAN_CHARACTERS_CSV, index=False)

    print("-" * 30)
    print(f"DONE! Saved to: {config.CLEAN_CHARACTERS_CSV}")
    print("Action: Open the file and verify the 'Unified_Name' column.")


if __name__ == "__main__":
    unify_names()