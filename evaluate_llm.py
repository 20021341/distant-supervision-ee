import json
import glob
import sys
import os

def evaluate_extracted_file(extracted_file, gold_file):
    print(f"Evaluating: {extracted_file}")
    print(f"Against gold: {gold_file}\n")

    # Load gold data
    gold_data = {}
    with open(gold_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                gold_data[rec["sent_id"]] = rec

    # Load extracted predictions
    pred_data = []
    with open(extracted_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                pred_data.append(json.loads(line))

    # Counters for the 3 tasks
    tp_emd, fp_emd, fn_emd = 0, 0, 0
    tp_ed, fp_ed, fn_ed = 0, 0, 0
    tp_eae, fp_eae, fn_eae = 0, 0, 0

    detail_file = extracted_file + ".eval_details.txt"
    
    print(f"Writing detailed differences to: {detail_file}")
    with open(detail_file, "w", encoding="utf-8") as out:
        out.write(f"Evaluation Details for: {extracted_file}\n")
        out.write(f"{'='*80}\n\n")

        for pred_rec in pred_data:
            sent_id = pred_rec["sent_id"]
            if sent_id not in gold_data:
                print(f"Warning: {sent_id} not found in gold data. Skipping.")
                continue

            gold_rec = gold_data[sent_id]
            sentence = gold_rec.get("sentence", "")

            # -------------------------------------------------------------
            # 1. EMD Evaluation
            # -------------------------------------------------------------
            gold_entities = set()
            gold_ent_str = {}
            for ent in gold_rec.get("entity_mentions", []):
                tup = (ent["start"], ent["end"], ent["entity_type"])
                gold_entities.add(tup)
                gold_ent_str[tup] = f"'{ent.get('text', '')}' ({ent['entity_type']})"

            pred_entities = set()
            pred_ent_str = {}
            for ent in pred_rec.get("entity_mentions", []):
                tup = (ent["start"], ent["end"], ent["entity_type"])
                pred_entities.add(tup)
                pred_ent_str[tup] = f"'{ent.get('text', '')}' ({ent['entity_type']})"

            emd_fn = gold_entities - pred_entities
            emd_fp = pred_entities - gold_entities
            
            tp_emd += len(gold_entities.intersection(pred_entities))
            fp_emd += len(emd_fp)
            fn_emd += len(emd_fn)

            # -------------------------------------------------------------
            # 2. ED Evaluation
            # -------------------------------------------------------------
            gold_events = set()
            gold_ev_str = {}
            for ev in gold_rec.get("event_mentions", []):
                trig = ev.get("trigger", {})
                tup = (trig.get("start"), trig.get("end"), ev["event_type"])
                gold_events.add(tup)
                gold_ev_str[tup] = f"'{trig.get('text', '')}' ({ev['event_type']})"

            pred_events = set()
            pred_ev_str = {}
            for ev in pred_rec.get("event_mentions", []):
                trig = ev.get("trigger", {})
                tup = (trig.get("start"), trig.get("end"), ev["event_type"])
                pred_events.add(tup)
                pred_ev_str[tup] = f"'{trig.get('text', '')}' ({ev['event_type']})"

            ed_fn = gold_events - pred_events
            ed_fp = pred_events - gold_events

            tp_ed += len(gold_events.intersection(pred_events))
            fp_ed += len(ed_fp)
            fn_ed += len(ed_fn)

            # -------------------------------------------------------------
            # 3. EAE Evaluation
            # -------------------------------------------------------------
            gold_ent_lookup = {ent["id"]: ent for ent in gold_rec.get("entity_mentions", [])}
            gold_args = set()
            gold_arg_str = {}
            for ev in gold_rec.get("event_mentions", []):
                ev_type = ev["event_type"]
                trig_text = ev.get("trigger", {}).get("text", "")
                for arg in ev.get("arguments", []):
                    ent_id = arg["entity_id"]
                    gold_ent = gold_ent_lookup.get(ent_id)
                    if gold_ent:
                        tup = (ev_type, gold_ent["start"], gold_ent["end"], arg["role"])
                        gold_args.add(tup)
                        gold_arg_str[tup] = f"Event: '{trig_text}' ({ev_type}) -> Arg: '{gold_ent.get('text','')}' [{arg['role']}]"

            pred_ent_lookup = {ent["id"]: ent for ent in pred_rec.get("entity_mentions", [])}
            pred_args = set()
            pred_arg_str = {}
            for ev in pred_rec.get("event_mentions", []):
                ev_type = ev["event_type"]
                trig_text = ev.get("trigger", {}).get("text", "")
                for arg in ev.get("arguments", []):
                    ent_id = arg["entity_id"]
                    pred_ent = pred_ent_lookup.get(ent_id)
                    if pred_ent:
                        tup = (ev_type, pred_ent["start"], pred_ent["end"], arg["role"])
                        pred_args.add(tup)
                        pred_arg_str[tup] = f"Event: '{trig_text}' ({ev_type}) -> Arg: '{pred_ent.get('text','')}' [{arg['role']}]"

            eae_fn = gold_args - pred_args
            eae_fp = pred_args - gold_args

            tp_eae += len(gold_args.intersection(pred_args))
            fp_eae += len(eae_fp)
            fn_eae += len(eae_fn)

            # --- WRITE LOG ---
            out.write(f"Doc ID: {sent_id}\n")
            out.write(f"Sentence: {sentence}\n\n")

            out.write("  [EMD - Entities]\n")
            out.write("    GROUND TRUTH: " + (", ".join([gold_ent_str[t] for t in gold_entities]) if gold_entities else "None") + "\n")
            out.write("    PREDICTED: " + (", ".join([pred_ent_str[t] for t in pred_entities]) if pred_entities else "None") + "\n")
            if emd_fn:
                out.write("    MISSING (FN): " + ", ".join([gold_ent_str[t] for t in emd_fn]) + "\n")
            if emd_fp:
                out.write("    INCORRECT/EXTRA (FP): " + ", ".join([pred_ent_str[t] for t in emd_fp]) + "\n")
            out.write("\n")

            out.write("  [ED - Event Triggers]\n")
            out.write("    GROUND TRUTH: " + (", ".join([gold_ev_str[t] for t in gold_events]) if gold_events else "None") + "\n")
            out.write("    PREDICTED: " + (", ".join([pred_ev_str[t] for t in pred_events]) if pred_events else "None") + "\n")
            if ed_fn:
                out.write("    MISSING (FN): " + ", ".join([gold_ev_str[t] for t in ed_fn]) + "\n")
            if ed_fp:
                out.write("    INCORRECT/EXTRA (FP): " + ", ".join([pred_ev_str[t] for t in ed_fp]) + "\n")
            out.write("\n")

            out.write("  [EAE - Arguments]\n")
            if gold_args:
                out.write("    GROUND TRUTH:\n")
                for t in gold_args: out.write(f"      - {gold_arg_str[t]}\n")
            else:
                out.write("    GROUND TRUTH: None\n")
            if pred_args:
                out.write("    PREDICTED:\n")
                for t in pred_args: out.write(f"      - {pred_arg_str[t]}\n")
            else:
                out.write("    PREDICTED: None\n")
            
            if eae_fn:
                out.write("    MISSING (FN):\n")
                for t in eae_fn: out.write(f"      - {gold_arg_str[t]}\n")
            if eae_fp:
                out.write("    INCORRECT/EXTRA (FP):\n")
                for t in eae_fp: out.write(f"      - {pred_arg_str[t]}\n")
            out.write("\n")

            out.write(f"{'-'*80}\n")

    # Compute F1 scores
    prec_emd, rec_emd, f1_emd = calculate_metrics(tp_emd, fp_emd, fn_emd)
    prec_ed, rec_ed, f1_ed = calculate_metrics(tp_ed, fp_ed, fn_ed)
    prec_eae, rec_eae, f1_eae = calculate_metrics(tp_eae, fp_eae, fn_eae)

    print("-" * 50)
    print(f"1. Entity Mention Detection (EMD)")
    print(f"   Precision: {prec_emd:.4f}")
    print(f"   Recall:    {rec_emd:.4f}")
    print(f"   F1 Score:  {f1_emd:.4f}\n")

    print(f"2. Event Detection (ED)")
    print(f"   Precision: {prec_ed:.4f}")
    print(f"   Recall:    {rec_ed:.4f}")
    print(f"   F1 Score:  {f1_ed:.4f}\n")

    print(f"3. Event Argument Extraction (EAE)")
    print(f"   Precision: {prec_eae:.4f}")
    print(f"   Recall:    {rec_eae:.4f}")
    print(f"   F1 Score:  {f1_eae:.4f}")
    print("-" * 50)

def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1

def get_latest_extracted_file():
    pattern = "final_data/processed_enriched_3/train_llm_extracted*.json"
    files = glob.glob(pattern)
    if not files:
        return None
    # Filter out empty files
    valid_files = [f for f in files if os.path.exists(f) and os.path.getsize(f) > 0]
    if not valid_files:
        return None
    return max(valid_files, key=os.path.getmtime)

if __name__ == "__main__":
    gold_file = "final_data/processed_enriched_3/train.json"
    
    if len(sys.argv) > 1:
        extracted_file = sys.argv[1]
    else:
        extracted_file = get_latest_extracted_file()
        if extracted_file is None:
            print("Error: No extracted JSON files found matching pattern.")
            sys.exit(1)

    evaluate_extracted_file(extracted_file, gold_file)
