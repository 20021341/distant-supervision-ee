import datetime
import json
import os
import re

# ----------------------------------------------------------------------
# Configurations
# ----------------------------------------------------------------------
INPUT_FILE = "final_data/processed_enriched_3/train.json"
MAX_SAMPLES = 100  # Set to None to run all sentences in the file

BASE_URL = "http://mac-tinix-kb.local:1234/v1"
API_KEY = "not-needed"
MODEL_NAME = "mlx-qwen3.5-4b-claude-4.6-opus-reasoning-distilled"

# Dynamic unique output filename
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = f"final_data/processed_enriched_3/train_llm_extracted_{timestamp}.json"


# ----------------------------------------------------------------------
# 1. Abbreviation & Full Name Type Mappings
# ----------------------------------------------------------------------
ENTITY_TYPE_MAPPING = {
    "PER": "Person",
    "ORG": "Organization",
    "GPE": "Geo-Political Entity",
    "LOC": "Location",
    "FAC": "Facility",
    "WEA": "Weapon",
    "VEH": "Vehicle",
    "TIME": "Time",
    "MONEY": "Money",
    "CRIME": "Crime",
    "SEN": "Sentence",
    "JOB": "Job"
}

EVENT_TYPE_MAPPING = {
    "Start-org": "Start-organization",
    "End-org": "End-organization",
    "Merge-org": "Merge-organization"
}

ROLE_MAPPING = {
    "Org": "Organization",
    "Loc": "Location",
    "Per": "Person",
    "Fac": "Facility",
    "Wea": "Weapon",
    "Veh": "Vehicle",
}

REVERSE_ENTITY_TYPE_MAPPING = {v.lower(): k for k, v in ENTITY_TYPE_MAPPING.items()}
for k, v in ENTITY_TYPE_MAPPING.items():
    REVERSE_ENTITY_TYPE_MAPPING[k.lower()] = k

REVERSE_EVENT_TYPE_MAPPING = {v.lower(): k for k, v in EVENT_TYPE_MAPPING.items()}
for k, v in EVENT_TYPE_MAPPING.items():
    REVERSE_EVENT_TYPE_MAPPING[k.lower()] = k

REVERSE_ROLE_MAPPING = {v.lower(): k for k, v in ROLE_MAPPING.items()}
for k, v in ROLE_MAPPING.items():
    REVERSE_ROLE_MAPPING[k.lower()] = k


# ----------------------------------------------------------------------
# 2. Dynamic Type Aggregation
# ----------------------------------------------------------------------
def aggregate_types_from_data(file_path):
    print(f"Scanning {file_path} to aggregate types...")
    entity_types = set()
    event_types = set()
    roles = set()

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                for ent in rec.get("entity_mentions", []):
                    entity_types.add(ent["entity_type"])
                for ev in rec.get("event_mentions", []):
                    event_types.add(ev["event_type"])
                    for arg in ev.get("arguments", []):
                        roles.add(arg["role"])
    except FileNotFoundError:
        print(f"File {file_path} not found. Using empty type lists.")

    print(f"Found {len(entity_types)} entity types, {len(event_types)} event types, and {len(roles)} argument roles.")
    return sorted(list(entity_types)), sorted(list(event_types)), sorted(list(roles))


# ----------------------------------------------------------------------
# 3. Token Matching & Span Computation
# ----------------------------------------------------------------------
def compute_token_spans(sentence, tokens):
    """
    Given the full sentence and the array of tokens,
    compute start and end char indices for each token.
    """
    spans = []
    current_pos = 0
    for t in tokens:
        start_idx = sentence.find(t, current_pos)
        if start_idx == -1:
            # Fallback if there's any mismatch
            start_idx = current_pos
        end_idx = start_idx + len(t)
        spans.append((start_idx, end_idx))
        current_pos = end_idx
    return spans


def char_span_to_token_span(start_char, end_char, token_spans):
    """
    Map character start and end to token indices in tokens array.
    """
    start_token = None
    end_token = None

    for i, (ts, te) in enumerate(token_spans):
        # If token overlaps or starts/ends near the char span
        if te > start_char and ts < end_char:
            if start_token is None:
                start_token = i
            end_token = i + 1

    # Fallback
    if start_token is None:
        start_token = 0
        end_token = 1
    elif end_token is None:
        end_token = start_token + 1

    return start_token, end_token


# ----------------------------------------------------------------------
# 4. LLM Interaction & Prompt Generation
# ----------------------------------------------------------------------
FEW_SHOT_EXAMPLES = """
Example 1:
Input Sentence: "Ngày 26/11 , Bộ Tài chính khai trương giao diện mới Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước ."
Output JSON:
{
  "entities": [
    {"text": "Ngày 26/11", "type": "Time"},
    {"text": "Bộ Tài chính", "type": "Organization"},
    {"text": "Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước", "type": "Organization"}
  ],
  "events": [
    {
      "trigger": "khai trương",
      "type": "Start-organization",
      "arguments": [
        {"text": "Bộ Tài chính", "role": "Agent"},
        {"text": "Ngày 26/11", "role": "Time"},
        {"text": "Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước", "role": "Org"}
      ]
    }
  ]
}

Example 2:
Input Sentence: "Ít nhất 10 người đã thiệt mạng và hàng chục người nhập viện trong các vụ bạo lực ở Thái Lan ."
Output JSON:
{
  "entities": [
    {"text": "10 người", "type": "Person"},
    {"text": "hàng chục người", "type": "Person"},
    {"text": "Thái Lan", "type": "Geo-Political Entity"}
  ],
  "events": [
    {
      "trigger": "thiệt mạng",
      "type": "Die",
      "arguments": [
        {"text": "10 người", "role": "Victim"}
      ]
    },
    {
      "trigger": "nhập viện",
      "type": "Injure",
      "arguments": [
        {"text": "hàng chục người", "role": "Victim"}
      ]
    },
    {
      "trigger": "bạo lực",
      "type": "Demonstrate",
      "arguments": [
        {"text": "Thái Lan", "role": "Place"}
      ]
    }
  ]
}

Example 3:
Input Sentence: "Ông Hưng nổ nhiều phát súng tại quán ăn đêm ."
Output JSON:
{
  "entities": [
    {"text": "súng", "type": "Weapon"},
    {"text": "Ông Hưng", "type": "Person"},
    {"text": "quán ăn đêm", "type": "Facility"}
  ],
  "events": [
    {
      "trigger": "nổ nhiều phát súng",
      "type": "Attack",
      "arguments": [
        {"text": "súng", "role": "Instrument"},
        {"text": "Ông Hưng", "role": "Attacker"},
        {"text": "quán ăn đêm", "role": "Place"}
      ]
    }
  ]
}

Example 4:
Input Sentence: "Ngân hàng cổ phần Bưu điện Liên Việt cũng báo cáo bằng văn bản với toà án đã khởi kiện Công ty PVC Land ."
Output JSON:
{
  "entities": [
    {"text": "Ngân hàng cổ phần Bưu điện Liên Việt", "type": "Organization"},
    {"text": "Công ty PVC Land", "type": "Organization"}
  ],
  "events": [
    {
      "trigger": "khởi kiện",
      "type": "Sue",
      "arguments": [
        {"text": "Ngân hàng cổ phần Bưu điện Liên Việt", "role": "Plaintiff"},
        {"text": "Công ty PVC Land", "role": "Defendant"}
      ]
    }
  ]
}
"""


def extract_events_with_llm(sentence, entity_types, event_types, roles):
    # Translate types to their full names for the LLM
    full_entity_types = sorted(list(set(ENTITY_TYPE_MAPPING.get(t, t) for t in entity_types)))
    full_event_types = sorted(list(set(EVENT_TYPE_MAPPING.get(t, t) for t in event_types)))
    full_roles = sorted(list(set(ROLE_MAPPING.get(t, t) for t in roles)))

    system_prompt = f"""You are a strict and precise Information Extraction AI for Vietnamese text.
Your task is to extract Entities, Event Triggers, and Argument Roles from the given sentence.

DEFINITIONS & RULES:
1. ENTITIES (Thực thể):
   - What: Specific named objects, persons, organizations, locations, times, or concepts.
   - Rule 1 (EXACT SPAN): Extract the FULL text exactly as it appears in the sentence (e.g., "trung tướng Thành", NOT just "Thành").
   - Rule 2 (TYPES): You MUST use ONLY these valid types: {full_entity_types}

2. EVENT TRIGGERS (Từ kích hoạt sự kiện):
   - What: The shortest keyword or verb phrase that clearly indicates the event happened.
   - Rule 1 (SHORTEST EXACT SPAN): Extract exactly as it appears. Do NOT extract long clauses (e.g., extract "ra" or "khai trương", NOT "từ quê ra thành phố").
   - Rule 2 (TYPES): You MUST use ONLY these valid event types: {full_event_types}

3. ARGUMENTS (Đối số):
   - What: How entities participate in the events.
   - Rule 1 (MATCH ENTITY): The argument "text" MUST exactly match one of the texts in your "entities" list.
   - Rule 2 (ROLES): You MUST use ONLY these valid argument roles: {full_roles}. NEVER invent new roles if they are not in this list.

OUTPUT FORMAT:
First, you may briefly analyze the sentence step-by-step.
Then, provide your final answer in a single JSON block wrapped in ```json ... ```:
{{
  "entities": [
    {{"text": "exact entity text from sentence", "type": "exact type from list"}}
  ],
  "events": [
    {{
      "trigger": "exact shortest trigger word from sentence",
      "type": "exact event type from list",
      "arguments": [
        {{"text": "must exactly match an entity text above", "role": "exact role from list"}}
      ]
    }}
  ]
}}

EXAMPLES:
{FEW_SHOT_EXAMPLES}
"""

    print(system_prompt)

    last_error = None
    raw_response = ""
    for attempt in range(3):
        try:
            from openai import OpenAI
            client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f'Input Sentence: "{sentence}"\nOutput JSON:'}
                ],
            )
            raw_response = response.choices[0].message.content
            content = raw_response.strip()
            # Clean potential markdown block fences if any
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                parts = content.split("```")
                for p in parts:
                    p_strip = p.strip()
                    if p_strip.startswith("{") and p_strip.endswith("}"):
                        content = p_strip
                        break
                else:
                    content = parts[1] if len(parts) > 1 else parts[0]

            # Fallback: Extract from the first '{' to the last '}'
            start_idx = content.find("{")
            end_idx = content.rfind("}")
            if start_idx != -1 and end_idx != -1:
                content = content[start_idx : end_idx + 1]

            parsed_json = json.loads(content.strip())
            return parsed_json, raw_response
        except Exception as e:
            print(f"Error calling OpenAI API on attempt {attempt + 1}: {e}")
            last_error = e

    return {"entities": [], "events": []}, f"All 3 attempts failed. Last error: {str(last_error)}. Raw response: {raw_response}"


# ----------------------------------------------------------------------
# 5. Post-Processing & Output Formulation
# ----------------------------------------------------------------------
def post_process_llm_output(llm_data, input_rec, token_spans, raw_response=None, valid_entity_types=None, valid_event_types=None, valid_roles=None):
    """
    Formulate the extracted information into the exact schema required for train.json.
    """
    sentence = input_rec["sentence"]
    doc_id = input_rec["doc_id"]
    sent_id = input_rec["sent_id"]

    # Deduplicate extracted entities by text to avoid identical spans
    extracted_entities = []
    seen_texts = set()
    for ent in llm_data.get("entities", []):
        t = ent.get("text", "").strip()
        tp = ent.get("type", "").strip()
        if not t or not tp:
            continue
        if (t, tp) not in seen_texts:
            seen_texts.add((t, tp))
            extracted_entities.append(ent)

    entity_mentions = []
    entity_text_to_id = {}

    for idx, ent in enumerate(extracted_entities):
        text = ent["text"]
        full_type = ent["type"]

        # Map back from full name to abbreviation
        mapped_type = REVERSE_ENTITY_TYPE_MAPPING.get(full_type.lower())
        if mapped_type is None:
            entity_type = full_type
        else:
            entity_type = mapped_type

        # Check OOV status
        is_oov = True
        if valid_entity_types and entity_type in valid_entity_types:
            is_oov = False

        # Find occurrence in sentence
        start_char = sentence.find(text)
        is_valid_text = True
        if start_char == -1:
            is_valid_text = False
            start_char = 0
            end_char = 0
            start_token = 0
            end_token = 0
        else:
            end_char = start_char + len(text)
            start_token, end_token = char_span_to_token_span(start_char, end_char, token_spans)

        ent_id = f"{sent_id}-T{idx + 1}"

        mention = {
            "id": ent_id,
            "text": text,
            "entity_type": entity_type,
            "start": start_token,
            "end": end_token,
            "start_char": start_char,
            "end_char": end_char,
            "mention_type": "UNK",
            "is_oov": is_oov,
            "is_valid_text": is_valid_text
        }
        entity_mentions.append(mention)
        entity_text_to_id[text] = ent_id

    # Post-process events
    event_mentions = []
    trigger_counter = len(entity_mentions) + 1

    for ev in llm_data.get("events", []):
        trigger_text = ev.get("trigger", "").strip()
        full_event_type = ev.get("type", "").strip()
        if not trigger_text or not full_event_type:
            continue

        # Map back from full name to abbreviation
        mapped_event_type = REVERSE_EVENT_TYPE_MAPPING.get(full_event_type.lower())
        if mapped_event_type is None:
            event_type = full_event_type
        else:
            event_type = mapped_event_type

        # Check OOV status
        is_oov_ev = True
        if valid_event_types and event_type in valid_event_types:
            is_oov_ev = False

        start_char = sentence.find(trigger_text)
        is_valid_ev_text = True
        if start_char == -1:
            is_valid_ev_text = False
            start_char = 0
            end_char = 0
            start_token = 0
            end_token = 0
        else:
            end_char = start_char + len(trigger_text)
            start_token, end_token = char_span_to_token_span(start_char, end_char, token_spans)

        event_id = f"{sent_id}-T{trigger_counter}"
        trigger_counter += 1

        arguments = []
        for arg in ev.get("arguments", []):
            arg_text = arg.get("text", "").strip()
            full_role = arg.get("role", "").strip()
            if not arg_text or not full_role:
                continue

            mapped_role = REVERSE_ROLE_MAPPING.get(full_role.lower())
            if mapped_role is None:
                role = full_role
            else:
                role = mapped_role

            # Check OOV status
            is_oov_arg = True
            if valid_roles and role in valid_roles:
                is_oov_arg = False

            is_valid_arg_text = (sentence.find(arg_text) != -1)

            # Check if this exact text is linked to an existing entity
            ent_id = entity_text_to_id.get(arg_text)

            # If not present in entities, dynamically add to entities (UNK) to keep it robust
            if ent_id is None:
                # Let's find its char span
                arg_sc = sentence.find(arg_text)
                if arg_sc != -1:
                    arg_ec = arg_sc + len(arg_text)
                    arg_st, arg_et = char_span_to_token_span(arg_sc, arg_ec, token_spans)
                    ent_id = f"{sent_id}-T{trigger_counter}"
                    trigger_counter += 1
                    implicit_mention = {
                        "id": ent_id,
                        "text": arg_text,
                        "entity_type": "UNK",
                        "start": arg_st,
                        "end": arg_et,
                        "start_char": arg_sc,
                        "end_char": arg_ec,
                        "mention_type": "UNK",
                        "is_oov": True,
                        "is_valid_text": True
                    }
                    entity_mentions.append(implicit_mention)
                    entity_text_to_id[arg_text] = ent_id
                else:
                    # Not found in text
                    ent_id = f"{sent_id}-T{trigger_counter}"
                    trigger_counter += 1
                    implicit_mention = {
                        "id": ent_id,
                        "text": arg_text,
                        "entity_type": "UNK",
                        "start": 0,
                        "end": 0,
                        "start_char": 0,
                        "end_char": 0,
                        "mention_type": "UNK",
                        "is_oov": True,
                        "is_valid_text": False
                    }
                    entity_mentions.append(implicit_mention)
                    entity_text_to_id[arg_text] = ent_id

            if ent_id:
                arguments.append({
                    "entity_id": ent_id,
                    "text": arg_text,
                    "role": role,
                    "is_oov": is_oov_arg,
                    "is_valid_text": is_valid_arg_text
                })

        event_mentions.append({
            "id": event_id,
            "event_type": event_type,
            "trigger": {
                "text": trigger_text,
                "start": start_token,
                "end": end_token,
                "start_char": start_char,
                "end_char": end_char
            },
            "arguments": arguments,
            "is_oov": is_oov_ev,
            "is_valid_text": is_valid_ev_text
        })

    # Preserve all other metadata from input_rec
    output_rec = {
        "doc_id": doc_id,
        "sent_id": sent_id,
        "tokens": input_rec["tokens"],
        "sentence": sentence,
        "pieces": input_rec.get("pieces", []),
        "token_lens": input_rec.get("token_lens", []),
        "entity_mentions": entity_mentions,
        "event_mentions": event_mentions,
        "relation_mentions": input_rec.get("relation_mentions", []),
        "raw_response": raw_response
    }
    return output_rec


# ----------------------------------------------------------------------
# 6. Evaluation Logic
# ----------------------------------------------------------------------
def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1

def evaluate_extracted_file(extracted_file, gold_file):
    print(f"\n--- Evaluation Results ---")
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

    for pred_rec in pred_data:
        sent_id = pred_rec["sent_id"]
        if sent_id not in gold_data:
            continue

        gold_rec = gold_data[sent_id]

        # 1. EMD Evaluation
        gold_entities = set()
        for ent in gold_rec.get("entity_mentions", []):
            gold_entities.add((ent["start"], ent["end"], ent["entity_type"]))

        pred_entities = set()
        for ent in pred_rec.get("entity_mentions", []):
            pred_entities.add((ent["start"], ent["end"], ent["entity_type"]))

        tp_emd += len(gold_entities.intersection(pred_entities))
        fp_emd += len(pred_entities - gold_entities)
        fn_emd += len(gold_entities - pred_entities)

        # 2. ED Evaluation
        gold_events = set()
        for ev in gold_rec.get("event_mentions", []):
            trig = ev.get("trigger", {})
            gold_events.add((trig["start"], trig["end"], ev["event_type"]))

        pred_events = set()
        for ev in pred_rec.get("event_mentions", []):
            trig = ev.get("trigger", {})
            pred_events.add((trig.get("start"), trig.get("end"), ev["event_type"]))

        tp_ed += len(gold_events.intersection(pred_events))
        fp_ed += len(pred_events - gold_events)
        fn_ed += len(gold_events - pred_events)

        # 3. EAE Evaluation
        gold_ent_lookup = {ent["id"]: ent for ent in gold_rec.get("entity_mentions", [])}
        gold_args = set()
        for ev in gold_rec.get("event_mentions", []):
            ev_type = ev["event_type"]
            for arg in ev.get("arguments", []):
                ent_id = arg["entity_id"]
                gold_ent = gold_ent_lookup.get(ent_id)
                if gold_ent:
                    gold_args.add((ev_type, gold_ent["start"], gold_ent["end"], arg["role"]))

        pred_ent_lookup = {ent["id"]: ent for ent in pred_rec.get("entity_mentions", [])}
        pred_args = set()
        for ev in pred_rec.get("event_mentions", []):
            ev_type = ev["event_type"]
            for arg in ev.get("arguments", []):
                ent_id = arg["entity_id"]
                pred_ent = pred_ent_lookup.get(ent_id)
                if pred_ent:
                    pred_args.add((ev_type, pred_ent["start"], pred_ent["end"], arg["role"]))

        tp_eae += len(gold_args.intersection(pred_args))
        fp_eae += len(pred_args - gold_args)
        fn_eae += len(gold_args - pred_args)

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

# ----------------------------------------------------------------------
# 7. Main Execution Flow
# ----------------------------------------------------------------------
def main():
    # 1. Aggregate entity types, event types, and argument roles dynamically
    entity_types, event_types, roles = aggregate_types_from_data(INPUT_FILE)

    if not entity_types or not event_types:
        print("Dynamic type extraction found no types. Aborting pipeline.")
        return

    print("Opening input file to begin extraction...")
    input_records = []
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    input_records.append(json.loads(line))
    except FileNotFoundError:
        print(f"Error: file {INPUT_FILE} not found.")
        return

    # Take the first MAX_SAMPLES if set
    total_records = len(input_records)
    if MAX_SAMPLES is not None:
        if MAX_SAMPLES < total_records:
            input_records = input_records[:MAX_SAMPLES]
        print(f"Running LLM extraction on the first {MAX_SAMPLES} out of {total_records} records.")
    else:
        print(f"Running LLM extraction on all {total_records} records.")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    print(f"Writing directly to {OUTPUT_FILE} line by line.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for idx, rec in enumerate(input_records):
            sentence = rec["sentence"]
            tokens = rec["tokens"]
            print(f"[{idx + 1}/{len(input_records)}] Processing sentence: {sentence[:70]}...")

            token_spans = compute_token_spans(sentence, tokens)
            llm_data, raw_res = extract_events_with_llm(sentence, entity_types, event_types, roles)
            processed_rec = post_process_llm_output(llm_data, rec, token_spans, raw_response=raw_res, valid_entity_types=entity_types, valid_event_types=event_types, valid_roles=roles)
            
            # Write immediately
            out.write(json.dumps(processed_rec, ensure_ascii=False) + "\n")
            out.flush()

    print(f"Completed! Output written to {OUTPUT_FILE}")

    # Evaluate immediately
    evaluate_extracted_file(OUTPUT_FILE, INPUT_FILE)

if __name__ == "__main__":
    main()
