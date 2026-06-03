import json
import glob
import sys
import os

def is_similar_text(t1, t2):
    t1_c = str(t1).strip().lower()
    t2_c = str(t2).strip().lower()
    if not t1_c or not t2_c:
        return False
    return (t1_c == t2_c) or (t1_c in t2_c) or (t2_c in t1_c)

def evaluate_extracted_file(extracted_file, gold_file):
    print(f"Evaluating: {extracted_file}")
    print(f"Against gold: {gold_file}\n")

    # Load gold data
    gold_data = {}
    import gzip
    open_func = gzip.open if gold_file.endswith(".gz") else open
    mode = "rt" if gold_file.endswith(".gz") else "r"
    with open_func(gold_file, mode, encoding="utf-8") as f:
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
            gold_ents = gold_rec.get("entity_mentions", [])
            pred_ents = pred_rec.get("entity_mentions", [])

            matched_gold_ent_indices = set()
            emd_tp_list = []
            emd_fp_list = []

            for p_idx, p in enumerate(pred_ents):
                p_text = p.get("text", "")
                p_type = p.get("entity_type", "")
                matched = False
                for g_idx, g in enumerate(gold_ents):
                    if g_idx in matched_gold_ent_indices:
                        continue
                    g_text = g.get("text", "")
                    g_type = g.get("entity_type", "")
                    if p_type == g_type and is_similar_text(p_text, g_text):
                        matched = True
                        emd_tp_list.append((p, g))
                        matched_gold_ent_indices.add(g_idx)
                        break
                if not matched:
                    emd_fp_list.append(p)

            emd_fn_list = [g for g_idx, g in enumerate(gold_ents) if g_idx not in matched_gold_ent_indices]

            tp_emd += len(emd_tp_list)
            fp_emd += len(emd_fp_list)
            fn_emd += len(emd_fn_list)

            # -------------------------------------------------------------
            # 2. ED Evaluation
            # -------------------------------------------------------------
            gold_events = gold_rec.get("event_mentions", [])
            pred_events = pred_rec.get("event_mentions", [])

            matched_gold_ev_indices = set()
            ed_tp_list = []
            ed_fp_list = []

            for p_idx, p in enumerate(pred_events):
                p_type = p.get("event_type", "")
                p_trig = p.get("trigger", {}).get("text", "")
                matched = False
                for g_idx, g in enumerate(gold_events):
                    if g_idx in matched_gold_ev_indices:
                        continue
                    g_type = g.get("event_type", "")
                    g_trig = g.get("trigger", {}).get("text", "")
                    if p_type == g_type and is_similar_text(p_trig, g_trig):
                        matched = True
                        ed_tp_list.append((p, g))
                        matched_gold_ev_indices.add(g_idx)
                        break
                if not matched:
                    ed_fp_list.append(p)

            ed_fn_list = [g for g_idx, g in enumerate(gold_events) if g_idx not in matched_gold_ev_indices]

            tp_ed += len(ed_tp_list)
            fp_ed += len(ed_fp_list)
            fn_ed += len(ed_fn_list)

            # -------------------------------------------------------------
            # 3. EAE Evaluation
            # -------------------------------------------------------------
            gold_args = []
            gold_ent_lookup = {ent["id"]: ent for ent in gold_ents}
            for ev in gold_events:
                ev_type = ev["event_type"]
                trig_text = ev.get("trigger", {}).get("text", "")
                for arg in ev.get("arguments", []):
                    ent_id = arg["entity_id"]
                    gold_ent = gold_ent_lookup.get(ent_id)
                    if gold_ent:
                        gold_args.append({
                            "event_type": ev_type,
                            "trig_text": trig_text,
                            "role": arg["role"],
                            "text": gold_ent.get("text", "")
                        })

            pred_args = []
            pred_ent_lookup = {ent["id"]: ent for ent in pred_ents}
            for ev in pred_events:
                ev_type = ev["event_type"]
                trig_text = ev.get("trigger", {}).get("text", "")
                for arg in ev.get("arguments", []):
                    ent_id = arg["entity_id"]
                    pred_ent = pred_ent_lookup.get(ent_id)
                    if pred_ent:
                        pred_args.append({
                            "event_type": ev_type,
                            "trig_text": trig_text,
                            "role": arg["role"],
                            "text": pred_ent.get("text", "")
                        })

            matched_gold_arg_indices = set()
            eae_tp_list = []
            eae_fp_list = []

            for p_idx, p in enumerate(pred_args):
                p_ev_type = p["event_type"]
                p_role = p["role"]
                p_text = p["text"]
                matched = False
                for g_idx, g in enumerate(gold_args):
                    if g_idx in matched_gold_arg_indices:
                        continue
                    g_ev_type = g["event_type"]
                    g_role = g["role"]
                    g_text = g["text"]
                    if p_ev_type == g_ev_type and p_role == g_role and is_similar_text(p_text, g_text):
                        matched = True
                        eae_tp_list.append((p, g))
                        matched_gold_arg_indices.add(g_idx)
                        break
                if not matched:
                    eae_fp_list.append(p)

            eae_fn_list = [g for g_idx, g in enumerate(gold_args) if g_idx not in matched_gold_arg_indices]

            tp_eae += len(eae_tp_list)
            fp_eae += len(eae_fp_list)
            fn_eae += len(eae_fn_list)

            # --- WRITE LOG ---
            out.write(f"Doc ID: {sent_id}\n")
            out.write(f"Sentence: {sentence}\n\n")

            out.write("  [EMD - Entities]\n")
            out.write("    GROUND TRUTH: " + (", ".join([f"'{g['text']}' ({g['entity_type']})" for g in gold_ents]) if gold_ents else "None") + "\n")
            out.write("    PREDICTED: " + (", ".join([f"'{p['text']}' ({p['entity_type']})" for p in pred_ents]) if pred_ents else "None") + "\n")
            if emd_fn_list:
                out.write("    MISSING (FN): " + ", ".join([f"'{g['text']}' ({g['entity_type']})" for g in emd_fn_list]) + "\n")
            if emd_fp_list:
                out.write("    INCORRECT/EXTRA (FP): " + ", ".join([f"'{p['text']}' ({p['entity_type']})" for p in emd_fp_list]) + "\n")
            out.write("\n")

            out.write("  [ED - Event Triggers]\n")
            out.write("    GROUND TRUTH: " + (", ".join([f"'{g.get('trigger', {}).get('text', '')}' ({g['event_type']})" for g in gold_events]) if gold_events else "None") + "\n")
            out.write("    PREDICTED: " + (", ".join([f"'{p.get('trigger', {}).get('text', '')}' ({p['event_type']})" for p in pred_events]) if pred_events else "None") + "\n")
            if ed_fn_list:
                out.write("    MISSING (FN): " + ", ".join([f"'{g.get('trigger', {}).get('text', '')}' ({g['event_type']})" for g in ed_fn_list]) + "\n")
            if ed_fp_list:
                out.write("    INCORRECT/EXTRA (FP): " + ", ".join([f"'{p.get('trigger', {}).get('text', '')}' ({p['event_type']})" for p in ed_fp_list]) + "\n")
            out.write("\n")

            out.write("  [EAE - Arguments]\n")
            if gold_args:
                out.write("    GROUND TRUTH:\n")
                for g in gold_args:
                    out.write(f"      - Event: '{g['trig_text']}' ({g['event_type']}) -> Arg: '{g['text']}' [{g['role']}]\n")
            else:
                out.write("    GROUND TRUTH: None\n")
            if pred_args:
                out.write("    PREDICTED:\n")
                for p in pred_args:
                    out.write(f"      - Event: '{p['trig_text']}' ({p['event_type']}) -> Arg: '{p['text']}' [{p['role']}]\n")
            else:
                out.write("    PREDICTED: None\n")
            
            if eae_fn_list:
                out.write("    MISSING (FN):\n")
                for g in eae_fn_list:
                    out.write(f"      - Event: '{g['trig_text']}' ({g['event_type']}) -> Arg: '{g['text']}' [{g['role']}]\n")
            if eae_fp_list:
                out.write("    INCORRECT/EXTRA (FP):\n")
                for p in eae_fp_list:
                    out.write(f"      - Event: '{p['trig_text']}' ({p['event_type']}) -> Arg: '{p['text']}' [{p['role']}]\n")
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
    gold_file = "final_data/processed_enriched_3/train.json.gz"
    if not os.path.exists(gold_file):
        gold_file = "final_data/processed_enriched_3/train.json"
    
    if len(sys.argv) > 1:
        extracted_file = sys.argv[1]
    else:
        extracted_file = get_latest_extracted_file()
        if extracted_file is None:
            print("Error: No extracted JSON files found matching pattern.")
            sys.exit(1)

    evaluate_extracted_file(extracted_file, gold_file)
