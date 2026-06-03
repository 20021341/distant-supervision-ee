import json
import os
import gzip

filepath = "final_data/processed_enriched_3/train.json.gz"
if not os.path.exists(filepath):
    filepath = "final_data/processed_enriched_3/train.json"

open_func = gzip.open if filepath.endswith(".gz") else open
mode = "rt" if filepath.endswith(".gz") else "r"
with open_func(filepath, mode, encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 10: break
        rec = json.loads(line)
        print("Sentence:", rec["sentence"])
        print("Entities:")
        for ent in rec.get("entity_mentions", []):
            print(f"  - {ent['text']} ({ent['entity_type']})")
        print("Events:")
        for ev in rec.get("event_mentions", []):
            print(f"  - {ev['trigger']['text']} ({ev['event_type']})")
            for arg in ev.get("arguments", []):
                print(f"    * {arg['text']} ({arg['role']})")
        print("-" * 50)
