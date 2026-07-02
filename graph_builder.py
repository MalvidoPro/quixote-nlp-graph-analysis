import json
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import config

# CONFIGURATION
# We can filter very weak connections here if we want,
# but usually it is better to export everything and filter in Gephi.
MIN_WEIGHT = 1


def build_graph():
    print(f"--- STEP 4: BUILDING GRAPH (NODES & EDGES) ---")

    # 1. INITIALIZE SENTIMENT ANALYZER
    print("Initializing VADER Sentiment Analyzer...")
    analyzer = SentimentIntensityAnalyzer()

    # 2. LOAD SENTENCES (The Sidecar)
    print(f"Loading {config.SENTENCES_JSON}...")
    try:
        with open(config.SENTENCES_JSON, 'r', encoding='utf-8') as f:
            chapter_sentences = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {config.SENTENCES_JSON}. Run Step 3 first.")
        return

    # 3. LOAD POSITIONS
    print(f"Loading {config.POSITIONS_JSON}...")
    try:
        with open(config.POSITIONS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {config.POSITIONS_JSON}.")
        return

    # Data structures to hold our graph
    # Node counts: {"don quixote": 2150, "sancho": 1800...}
    node_counts = {}

    # Edge data: {("don quixote", "sancho panza"): {'weight': 540, 'sentiment_sum': 12.5}, ...}
    # We use a tuple (Source, Target) as the key.
    edge_data = {}

    print("Calculating interactions (Window: 15 words OR Same Sentence)...")

    # 4. ITERATE THROUGH CHAPTERS
    for chapter, events in data.items():
        # Retrieve text list for this chapter
        if chapter not in chapter_sentences:
            continue
        text_list = chapter_sentences[chapter]

        # Sort events by position just to be safe
        events.sort(key=lambda x: x['start'])

        num_events = len(events)

        for i in range(num_events):
            char_a = events[i]
            name_a = char_a['name']

            # Update Node Count (Frequency)
            node_counts[name_a] = node_counts.get(name_a, 0) + 1

            # LOOK AHEAD LOOP
            for j in range(i + 1, num_events):
                char_b = events[j]
                name_b = char_b['name']

                # --- FIX: PREVENT SELF-LOOPS ---
                if name_a == name_b:
                    continue

                # Logic 1: Same Sentence
                is_same_sentence = (char_b['sentence'] == char_a['sentence'])

                # Logic 2: Proximity (Word Distance)
                distance = char_b['start'] - char_a['end']

                if is_same_sentence or distance <= 15:
                    # VALID CONNECTION

                    # Sort names alphabetically to ensure A->B and B->A are stored as the same edge
                    # e.g. "Sancho"-"Quixote" becomes "Quixote"-"Sancho"
                    if name_a < name_b:
                        source, target = name_a, name_b
                    else:
                        source, target = name_b, name_a

                    edge_key = (source, target)

                    # Initialize dictionary for this pair if it doesn't exist
                    if edge_key not in edge_data:
                        edge_data[edge_key] = {'weight': 0, 'sentiment_sum': 0.0}

                    # Update Weight
                    edge_data[edge_key]['weight'] += 1

                    # Update Sentiment
                    # We grab the text of the sentence where Char A appears.
                    sent_idx = char_a['sentence']

                    if sent_idx < len(text_list):
                        sentence_text = text_list[sent_idx]
                        score = analyzer.polarity_scores(sentence_text)['compound']
                        edge_data[edge_key]['sentiment_sum'] += score

                else:
                    # OPTIMIZATION:
                    # If they are too far apart (and sentence index is different),
                    # stop checking this chain.
                    break

    # 5. EXPORT NODES
    print(f"Exporting Nodes...")
    nodes_list = []
    for name, count in node_counts.items():
        nodes_list.append({
            "Id": name,
            "Label": name.title(),  # Capitalize for nice display
            "Weight": count  # This will determine the size of the circle
        })

    df_nodes = pd.DataFrame(nodes_list)
    # Sort by most frequent characters
    df_nodes = df_nodes.sort_values(by="Weight", ascending=False)
    df_nodes.to_csv(config.NODES_CSV, index=False)

    # 6. EXPORT EDGES
    print(f"Exporting Edges...")
    edges_list = []
    for (source, target), stats in edge_data.items():
        weight = stats['weight']

        if weight >= MIN_WEIGHT:
            # Calculate Average Sentiment
            avg_sentiment = stats['sentiment_sum'] / weight

            edges_list.append({
                "Source": source,
                "Target": target,
                "Weight": weight,
                "Avg_Sentiment": round(avg_sentiment, 4),
                "Type": "Undirected"  # Gephi needs this to know lines don't have arrows
            })

    df_edges = pd.DataFrame(edges_list)
    # Sort by strongest connections
    df_edges = df_edges.sort_values(by="Weight", ascending=False)
    df_edges.to_csv(config.EDGES_CSV, index=False)

    print("-" * 30)
    print(f"DONE!")
    print(f"Nodes: {len(df_nodes)} saved to {config.NODES_CSV}")
    print(f"Edges: {len(df_edges)} saved to {config.EDGES_CSV}")


if __name__ == "__main__":
    build_graph()