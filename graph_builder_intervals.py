import json
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import config

# CONFIGURATION
MIN_WEIGHT = 1


def get_interval_label(chapter_number):
    """
    Finds which custom interval a chapter belongs to.
    Returns the label (e.g., "01. First Sortie") or None if not found.
    """
    for start, end, label in config.CHAPTER_RANGES:
        if start <= chapter_number <= end:
            return label
    return None


def build_graph():
    print(f"--- STEP 4: BUILDING EVOLUTIONARY GRAPH ---")

    # 1. SETUP
    print("Initializing VADER...")
    analyzer = SentimentIntensityAnalyzer()

    print(f"Loading data...")
    try:
        with open(config.SENTENCES_JSON, 'r', encoding='utf-8') as f:
            chapter_sentences = json.load(f)
        with open(config.POSITIONS_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: Missing input files.")
        return

    # Key: (Source, Target, Interval_Label)
    # By including the Interval in the key, we automatically "reset"
    # the count to 0 when the loop moves to a new interval.
    edge_data = {}

    # We also track nodes per interval so we can hide characters who don't appear in that book part
    node_data = {}  # Key: (Name, Interval_Label) -> count

    print(f"Processing chapters using custom ranges from config...")

    # 2. ITERATE
    for chapter_key, events in data.items():
        if chapter_key not in chapter_sentences: continue

        # Extract Absolute Chapter Number (Assumes key format "001_Chapter...")
        try:
            chap_num = int(chapter_key.split('_')[0])
        except ValueError:
            print(f"Skipping weird key: {chapter_key}")
            continue

        # IDENTIFY INTERVAL
        interval_label = get_interval_label(chap_num)

        # If this chapter isn't in any defined range, skip it
        if not interval_label:
            continue

        text_list = chapter_sentences[chapter_key]
        events.sort(key=lambda x: x['start'])

        num_events = len(events)

        for i in range(num_events):
            char_a = events[i]

            # Update Node Count specific to this Interval
            node_key = (char_a['name'], interval_label)
            node_data[node_key] = node_data.get(node_key, 0) + 1

            # Look Ahead
            for j in range(i + 1, num_events):
                char_b = events[j]

                if char_a['name'] == char_b['name']: continue

                is_same_sent = (char_b['sentence'] == char_a['sentence'])
                distance = char_b['start'] - char_a['end']

                if is_same_sent or distance <= 15:
                    p1, p2 = sorted((char_a['name'], char_b['name']))

                    # UNIQUE KEY: Source + Target + Interval
                    # This ensures weights don't carry over between intervals.
                    edge_key = (p1, p2, interval_label)

                    if edge_key not in edge_data:
                        edge_data[edge_key] = {'weight': 0, 'sentiment_sum': 0.0}

                    edge_data[edge_key]['weight'] += 1

                    # Add Sentiment
                    sent_idx = char_a['sentence']
                    if sent_idx < len(text_list):
                        score = analyzer.polarity_scores(text_list[sent_idx])['compound']
                        edge_data[edge_key]['sentiment_sum'] += score
                else:
                    break

    # 3. EXPORT EDGES
    print("Exporting Edges...")
    edges_list = []
    for (src, tgt, interval), stats in edge_data.items():
        w = stats['weight']
        if w >= MIN_WEIGHT:
            avg_sent = stats['sentiment_sum'] / w
            edges_list.append({
                "Source": src,
                "Target": tgt,
                "Weight": w,
                "Avg_Sentiment": round(avg_sent, 4),
                "Type": "Undirected",
                "Interval": interval  # Use this column in Gephi to filter
            })

    # 4. EXPORT NODES
    # We export nodes with their interval too, so you can filter nodes that don't exist in that part
    print("Exporting Nodes...")
    nodes_list = []
    for (name, interval), count in node_data.items():
        nodes_list.append({
            "Id": name,
            "Label": name.title(),
            "Weight": count,
            "Interval": interval
        })

    # Save to files
    pd.DataFrame(nodes_list).to_csv(config.NODES_EVOLUTION_CSV, index=False)
    pd.DataFrame(edges_list).to_csv(config.EDGES_EVOLUTION_CSV, index=False)

    print("-" * 30)
    print("DONE!")
    print(f"Saved: step4_nodes_evolution.csv ({len(nodes_list)} rows)")
    print(f"Saved: step4_edges_evolution.csv ({len(edges_list)} rows)")
    print("IN GEPHI: Import both files, then use 'Filters -> Attributes -> Partition -> Interval'")


if __name__ == "__main__":
    build_graph()