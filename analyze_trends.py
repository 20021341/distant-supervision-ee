import json
from collections import defaultdict
import numpy as np
from trend_detection import detect_trends_sliding

# 1. Load result.json using JSONDecoder to correctly parse sequential pretty JSON objects
def load_records(filepath):
    print(f"Reading records from {filepath}...")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    decoder = json.JSONDecoder()
    pos = 0
    records = []
    while pos < len(content):
        while pos < len(content) and content[pos].isspace():
            pos += 1
        if pos >= len(content):
            break
        obj, pos = decoder.raw_decode(content, pos)
        records.append(obj)
    print(f"Successfully loaded {len(records)} records.")
    return records

def main():
    records = load_records("result.json")
    
    # Dates of interest
    days = ['2025-03-07', '2025-03-08', '2025-03-09', '2025-03-10', '2025-03-11', '2025-03-12', '2025-03-13']
    
    # 2. Count events per day
    # day_event_counts[event_type][date] = count
    day_event_counts = defaultdict(lambda: defaultdict(int))
    for r in records:
        d = r.get('date')
        if d in days:
            for ev in r.get('event_mentions', []):
                day_event_counts[ev['event_type']][d] += 1
                
    # 3. Perform trend detection
    print("\n" + "="*80)
    print(f"{'Event Type':<25} | {'Weekly Counts':<25} | {'Trending Day':<12} | {'Max Score':<10}")
    print("="*80)
    
    results_summary = []
    for ev_type in sorted(day_event_counts.keys()):
        counts = [day_event_counts[ev_type][d] for d in days]
        trending_day, max_score = detect_trends_sliding(counts)
        results_summary.append({
            'event_type': ev_type,
            'counts': counts,
            'trending_day': trending_day,
            'max_score': max_score
        })
        
        counts_str = str(counts)
        day_str = f"Day {trending_day}" if trending_day is not None else "None"
        score_str = f"{max_score:.2f}" if max_score > -1 else "N/A"
        print(f"{ev_type:<25} | {counts_str:<25} | {day_str:<12} | {score_str:<10}")

    # 4. Filter only trending events and print them specifically
    print("\n" + "="*80)
    print("✨ DETECTED TRENDING EVENTS ✨")
    print("="*80)
    has_trends = False
    for r in results_summary:
        if r['trending_day'] is not None:
            has_trends = True
            print(f"🚀 Event '{r['event_type']}' peaked on Day {r['trending_day']} ({days[r['trending_day']-1]}) with a score of {r['max_score']:.2f}")
            print(f"   Counts: {r['counts']}")
            
    if not has_trends:
        print("No specific trends detected with the default threshold.")

if __name__ == "__main__":
    main()
