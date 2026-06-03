import datetime
import json
import os
import difflib
from concurrent.futures import ThreadPoolExecutor

# Try to load env variables from .env file manually if python-dotenv is not installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip("'\"")
                    os.environ[key] = val

# ----------------------------------------------------------------------
# Configurations
# ----------------------------------------------------------------------
# Support both .json.gz and .json fallback
INPUT_FILE = "final_data/processed_enriched_med/train_hanoi_national.json.gz"
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = "final_data/processed_enriched_med/train_hanoi_national.json"

SCHEMA_FILE = "med_schema.json" # Đổi tên file schema
MAX_SAMPLES = None
NUM_THREADS = 20
TEMPERATURE = 0.0

BASE_URL = "https://openrouter.ai/api/v1"
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "google/gemma-4-26b-a4b-it"

from openai import OpenAI
try:
    if not API_KEY:
        print("Warning: OPENROUTER_API_KEY environment variable is not set.")
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    client = None

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = f"final_data/processed_enriched_med/train_llm_extracted_med_v1_{timestamp}.json"


# ----------------------------------------------------------------------
# 1. Load Dynamic Schema & Descriptions from med_schema.json
# ----------------------------------------------------------------------
with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
    SCHEMA_DATA = json.load(f)

# Global dictionaries for descriptions populated from schema
ENTITY_TYPE_DESCRIPTIONS = {}
EVENT_TYPE_DESCRIPTIONS = {}
ROLE_DESCRIPTIONS = {}

def get_types_from_schema():
    print(f"Loading valid types and descriptions directly from {SCHEMA_FILE}...")
    
    entity_types = []
    for ent in SCHEMA_DATA.get("entities", []):
        name = ent.get("name")
        ENTITY_TYPE_DESCRIPTIONS[name] = ent.get("description", "")
        entity_types.append(name)
        
    roles = []
    for arg in SCHEMA_DATA.get("arguments", []):
        name = arg.get("name")
        ROLE_DESCRIPTIONS[name] = arg.get("description", "")
        roles.append(name)
        
    event_types = []
    for evt_name, evt_data in SCHEMA_DATA.get("events", {}).items():
        EVENT_TYPE_DESCRIPTIONS[evt_name] = evt_data.get("description", "")
        event_types.append(evt_name)
        
    print(f"Loaded {len(entity_types)} entity types, {len(event_types)} event types, and {len(roles)} argument roles strictly from Schema.")
    return sorted(entity_types), sorted(event_types), sorted(roles)


# ----------------------------------------------------------------------
# 2. Token Matching & Span Computation
# ----------------------------------------------------------------------
def compute_token_spans(sentence, tokens):
    spans = []
    current_pos = 0
    normalized_sentence = " ".join(sentence.split())
    for t in tokens:
        clean_t = t.replace("_", " ")
        start_idx = normalized_sentence.find(clean_t, current_pos)
        if start_idx == -1:
            start_idx = current_pos
        end_idx = start_idx + len(clean_t)
        spans.append((start_idx, end_idx))
        current_pos = end_idx
    return spans

def char_span_to_token_span(start_char, end_char, token_spans):
    start_token = None
    end_token = None
    for i, (ts, te) in enumerate(token_spans):
        if te > start_char and ts < end_char:
            if start_token is None:
                start_token = i
            end_token = i + 1
    if start_token is None:
        start_token = 0
        end_token = 1
    elif end_token is None:
        end_token = start_token + 1
    return start_token, end_token

def find_available_span(sentence, text, used_spans):
    start_char = sentence.find(text)
    if start_char == -1:
        return -1, -1
    best_start = start_char
    while start_char != -1:
        end_char = start_char + len(text)
        overlap = False
        for (us, ue) in used_spans:
            if max(start_char, us) < min(end_char, ue):
                overlap = True
                break
        if not overlap:
            return start_char, end_char
        start_char = sentence.find(text, start_char + 1)
    return best_start, best_start + len(text)


# ----------------------------------------------------------------------
# 3. Medical Domain Prompt Templates
# ----------------------------------------------------------------------

FEW_SHOT_ENTITIES = """\
Example 1:
Input Sentence: "Bệnh nhân nam 45 tuổi nhập viện vì sốt cao liên tục và ho khan kéo dài 3 ngày ."
Output JSON:
{
  "thought": "Let's identify medical entities. 'Bệnh nhân nam' refers to the patient -> Person:Patient. '45 tuổi' -> Temporal:Duration (or Age). 'sốt cao liên tục' and 'ho khan' are clinical symptoms -> Symptom:Physical. '3 ngày' is a duration -> Temporal:Duration. We must extract all these distinct clinical facts.",
  "entities": [
    {"text": "Bệnh nhân nam", "type": "Person:Patient"},
    {"text": "sốt cao liên tục", "type": "Symptom:Physical"},
    {"text": "ho khan", "type": "Symptom:Physical"},
    {"text": "3 ngày", "type": "Temporal:Duration"}
  ]
}

Example 2:
Input Sentence: "Bác sĩ Nguyễn Văn A chỉ định siêu âm ổ bụng và xét nghiệm máu tĩnh mạch , kết quả bạch cầu tăng 15 G/L ."
Output JSON:
{
  "thought": "Identify all clinical entities. 'Bác sĩ Nguyễn Văn A' is the healthcare provider -> Person:Clinician. 'siêu âm' is an imaging test -> Test:Imaging. 'ổ bụng' is a body part -> Anatomy:Body-Part. 'xét nghiệm máu' is a lab test -> Test:Lab-Test. 'tĩnh mạch' -> Anatomy:Body-Part. 'bạch cầu' -> Biomarker:Cell (or Biomarker:Protein/Gene depending on schema, here we map to Finding/Biomarker context, assume Finding:Lab-Result). 'tăng 15 G/L' is the test result -> Finding:Lab-Result.",
  "entities": [
    {"text": "Bác sĩ Nguyễn Văn A", "type": "Person:Clinician"},
    {"text": "siêu âm", "type": "Test:Imaging"},
    {"text": "ổ bụng", "type": "Anatomy:Body-Part"},
    {"text": "xét nghiệm máu", "type": "Test:Lab-Test"},
    {"text": "tĩnh mạch", "type": "Anatomy:Body-Part"},
    {"text": "bạch cầu tăng 15 G/L", "type": "Finding:Lab-Result"}
  ]
}

Example 3:
Input Sentence: "Cho bệnh nhân uống Paracetamol 500mg mỗi 6 giờ để giảm đau đầu ."
Output JSON:
{
  "thought": "Extract medication and clinical elements. 'bệnh nhân' -> Person:Patient. 'uống' is the administration route -> Route. 'Paracetamol' is the medication -> Substance:Drug. '500mg' is the amount -> Dosage. 'mỗi 6 giờ' -> Temporal:Frequency. 'đau đầu' -> Symptom:Physical.",
  "entities": [
    {"text": "bệnh nhân", "type": "Person:Patient"},
    {"text": "uống", "type": "Route"},
    {"text": "Paracetamol", "type": "Substance:Drug"},
    {"text": "500mg", "type": "Dosage"},
    {"text": "mỗi 6 giờ", "type": "Temporal:Frequency"},
    {"text": "đau đầu", "type": "Symptom:Physical"}
  ]
}
"""

FEW_SHOT_TRIGGERS = """\
Example 1:
Input Sentence: "Bệnh nhân nam 45 tuổi nhập viện vì sốt cao liên tục ."
Output JSON:
{
  "thought": "Find event triggers. 'nhập viện' (hospital admission) is the key action signaling a clinical encounter -> Clinical-Encounter:Admission. 'sốt cao' is a symptom, indicating the onset of a condition -> Disease-Progression:Onset.",
  "events": [
    {"trigger": "nhập viện", "type": "Clinical-Encounter:Admission"},
    {"trigger": "sốt cao", "type": "Disease-Progression:Onset"}
  ]
}

Example 2:
Input Sentence: "Bác sĩ kê đơn Paracetamol và dặn bệnh nhân tái khám sau 1 tuần ."
Output JSON:
{
  "thought": "Find event signals. 'kê đơn' (prescribe) signals ordering medication -> Treatment-Event:Prescribe. 'tái khám' (follow-up visit) signals a subsequent encounter -> Clinical-Encounter:Follow-Up.",
  "events": [
    {"trigger": "kê đơn", "type": "Treatment-Event:Prescribe"},
    {"trigger": "tái khám", "type": "Clinical-Encounter:Follow-Up"}
  ]
}

Example 3:
Input Sentence: "Bệnh nhân được phẫu thuật cắt bỏ ruột thừa , sau đó tình trạng viêm đã thuyên giảm rõ rệt ."
Output JSON:
{
  "thought": "Find event triggers. 'phẫu thuật' (surgery) signals an operative procedure -> Treatment-Event:Perform-Surgery. 'thuyên giảm' (remission/improvement) signals a positive change in disease state -> Disease-Progression:Improve.",
  "events": [
    {"trigger": "phẫu thuật", "type": "Treatment-Event:Perform-Surgery"},
    {"trigger": "thuyên giảm", "type": "Disease-Progression:Improve"}
  ]
}
"""

FEW_SHOT_ARGUMENTS = """\
Example 1:
Sentence: "Bệnh nhân nam 45 tuổi nhập viện vì sốt cao liên tục tại Bệnh viện Bạch Mai ."
Event Type: "Clinical-Encounter:Admission"
Event Trigger: "nhập viện"
Candidate Entities: [{"text": "Bệnh nhân nam", "type": "Person:Patient"}, {"text": "sốt cao liên tục", "type": "Symptom:Physical"}, {"text": "Bệnh viện Bạch Mai", "type": "Organization:Hospital"}]
Output JSON:
{
  "thought": "The event is 'Admission' triggered by 'nhập viện'. 1) 'Bệnh nhân nam' is the subject who is admitted -> Patient. 2) 'sốt cao liên tục' is the reason/cause for admission, but check if the schema allows Symptom for Admission. If yes, map to Symptom/Disease. 3) 'Bệnh viện Bạch Mai' is the location of the admission -> Place/Institution.",
  "arguments": [
    {"text": "Bệnh nhân nam", "role": "Patient"},
    {"text": "sốt cao liên tục", "role": "Symptom"},
    {"text": "Bệnh viện Bạch Mai", "role": "Institution"}
  ]
}

Example 2:
Sentence: "Cho bệnh nhân uống Paracetamol 500mg mỗi 6 giờ ."
Event Type: "Treatment-Event:Administer"
Event Trigger: "uống"
Candidate Entities: [{"text": "bệnh nhân", "type": "Person:Patient"}, {"text": "Paracetamol", "type": "Substance:Drug"}, {"text": "500mg", "type": "Dosage"}, {"text": "mỗi 6 giờ", "type": "Temporal:Frequency"}]
Output JSON:
{
  "thought": "The event is 'Administer' triggered by 'uống'. 1) 'bệnh nhân' is receiving the drug -> Patient. 2) 'Paracetamol' is the drug administered -> Substance. 3) '500mg' directly modifies the amount -> Dosage. 4) 'mỗi 6 giờ' directly modifies the frequency -> Time.",
  "arguments": [
    {"text": "bệnh nhân", "role": "Patient"},
    {"text": "Paracetamol", "role": "Substance"},
    {"text": "500mg", "role": "Dosage"},
    {"text": "mỗi 6 giờ", "role": "Time"}
  ]
}
"""


def _parse_llm_json(raw_response):
    content = raw_response.strip()
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
    start_idx = content.find("{")
    end_idx = content.rfind("}")
    if start_idx != -1 and end_idx != -1:
        content = content[start_idx: end_idx + 1]
    return json.loads(content.strip())


# ----------------------------------------------------------------------
# 4. LLM Extraction Functions (Medical Domain)
# ----------------------------------------------------------------------

def extract_entities_with_llm(sentence, entity_types):
    valid_entity_types_str = ""
    for et in entity_types:
        desc = ENTITY_TYPE_DESCRIPTIONS.get(et, "No description available.")
        valid_entity_types_str += f"- **{et}**: {desc}\n"

    system_prompt = f"""You are a highly precise Medical Named Entity Recognition (NER) AI for Vietnamese clinical text.
Your task is to identify and extract ALL medical and clinical entity mentions from the given Vietnamese sentence.

VALID ENTITY TYPES WITH DEFINITIONS:
{valid_entity_types_str}

EXTRACTION RULES:
1. Extract each entity text span EXACTLY as it appears in the sentence.
2. Assign ONLY types from the VALID ENTITY TYPES list above.
3. BE COMPREHENSIVE AND MAXIMIZE RECALL: Ensure you extract all symptoms, diseases, drugs, dosages, routes, test names, lab results, body parts, patients, and clinicians.
   - MEDICATION RULE: Extract exact drug names (e.g., Paracetamol, Aspirin), dosages (e.g., 500mg, 2 viên), and routes (e.g., uống, tiêm tĩnh mạch).
   - FINDING/SYMPTOM RULE: Extract complete phrases for symptoms and lab results (e.g., "sốt cao 39 độ", "bạch cầu tăng 15 G/L", "đau quặn bụng").
   - ANATOMY RULE: Extract specific body parts and organs mentioned (e.g., "ổ bụng", "gan", "mạch máu").
4. CRITICAL: Write a highly detailed "thought" in English BEFORE listing entities. Analyze the sentence word-by-word against the clinical definitions.
5. If no entities are found, return an empty list.

OUTPUT FORMAT (strict JSON only):
{{
  "thought": "Step-by-step clinical reasoning...",
  "entities": [
    {{"text": "exact text from sentence", "type": "type from valid list"}}
  ]
}}

EXAMPLES:
{FEW_SHOT_ENTITIES}
"""
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f'Input Sentence: "{sentence}"\nOutput JSON:'}
                ],
                response_format={"type": "json_object"},
                temperature=TEMPERATURE
            )
            parsed_json = _parse_llm_json(response.choices[0].message.content)
            return parsed_json.get("entities", [])
        except Exception as e:
            print(f"  [Entity Extraction] Error on attempt {attempt + 1}: {e}")
    return []


def extract_event_triggers_with_llm(sentence, event_types):
    valid_event_types_str = ""
    for evt in event_types:
        desc = EVENT_TYPE_DESCRIPTIONS.get(evt, "No description available.")
        valid_event_types_str += f"- **{evt}**: {desc}\n"

    system_prompt = f"""You are a Medical Event Detection AI for Vietnamese clinical text.
Your task is to identify and extract ALL clinical event triggers from the given Vietnamese sentence.

VALID EVENT TYPES WITH DEFINITIONS:
{valid_event_types_str}

EXTRACTION RULES:
1. Extract the shortest keyword, verb, or action noun phrase that DIRECTLY signals an event of a valid clinical type.
2. The trigger must be found verbatim in the sentence.
3. Assign ONLY types from the VALID EVENT TYPES list above.
4. BE COMPREHENSIVE: Capture verbs indicating hospital admissions (nhập viện), discharges (xuất viện), procedures (phẫu thuật, siêu âm, xét nghiệm), medication administration (uống, tiêm, kê đơn), and disease progression (khởi phát, thuyên giảm, tử vong).
5. Write a detailed "thought" in English analyzing the clinical verbs/states.

OUTPUT FORMAT (strict JSON only):
{{
  "thought": "Step-by-step clinical reasoning...",
  "events": [
    {{"trigger": "exact trigger word", "type": "exact event type"}}
  ]
}}

EXAMPLES:
{FEW_SHOT_TRIGGERS}
"""
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f'Input Sentence: "{sentence}"\nOutput JSON:'}
                ],
                response_format={"type": "json_object"},
                temperature=TEMPERATURE
            )
            parsed_json = _parse_llm_json(response.choices[0].message.content)
            return parsed_json.get("events", [])
        except Exception as e:
            print(f"  [Trigger Extraction] Error on attempt {attempt + 1}: {e}")
    return []


def extract_event_arguments_with_llm(sentence, event_type, trigger, entities, roles):
    event_schema = SCHEMA_DATA["events"].get(event_type, {}).get("schema", {})
    allowed_roles = list(event_schema.keys())

    valid_roles_str = ""
    for r in allowed_roles:
        desc = ROLE_DESCRIPTIONS.get(r, "No description available.")
        valid_roles_str += f"- **{r}**: {desc}\n"
    
    role_schema_hint = f"For the '{event_type}' event, allowed roles and compatible entity types:\n"
    for r, allowed_ents in event_schema.items():
        role_schema_hint += f"  - **{r}** (Accepts: {', '.join(allowed_ents)})\n"

    system_prompt = f"""You are a Clinical Event Argument Extraction AI for Vietnamese text.
Given a sentence with an identified medical event, select ONLY the candidate entities that DIRECTLY fill the argument roles of THAT SPECIFIC event trigger.

SENTENCE: "{sentence}"
EVENT TYPE: "{event_type}"
EVENT TRIGGER: "{trigger}"
CANDIDATE ENTITIES WITH TYPES: {json.dumps(entities, ensure_ascii=False)}

EVENT SCHEMAS:
{role_schema_hint}

VALID ARGUMENT ROLES:
{valid_roles_str}

CRITICAL RULES:
1. **DIRECT-LINK PRINCIPLE**: The entity MUST have a direct grammatical/semantic link to the medical trigger "{trigger}".
2. Assign each selected entity exactly ONE valid role.
3. Ensure the entity's type is explicitly allowed for the assigned role per the EVENT SCHEMAS.
4. If NO candidate satisfies a role, leave it EMPTY. Do not force incorrect associations.
5. Write a detailed "thought" explaining the grammatical relationship.

OUTPUT FORMAT (strict JSON only):
{{
  "thought": "Role analysis...",
  "arguments": [
    {{"text": "candidate text", "role": "role name"}}
  ]
}}

EXAMPLES:
{FEW_SHOT_ARGUMENTS}
"""
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f'Assign roles for "{event_type}" triggered by "{trigger}":\nOutput JSON:'}
                ],
                response_format={"type": "json_object"},
                temperature=TEMPERATURE
            )
            parsed_json = _parse_llm_json(response.choices[0].message.content)
            raw_arguments = parsed_json.get("arguments", [])

            valid_arguments = []
            entity_type_map = {ent["text"].lower().strip(): ent["type"] for ent in entities}
            
            for arg in raw_arguments:
                text = arg.get("text", "").strip()
                role = arg.get("role", "").strip()
                if not text or not role: continue
                
                if role not in event_schema:
                    matched_role = next((sr for sr in event_schema.keys() if sr.lower() == role.lower()), None)
                    if matched_role: role = matched_role
                    else: continue
                
                ent_type = entity_type_map.get(text.lower())
                if not ent_type:
                    for cand_text, cand_type in entity_type_map.items():
                        if text.lower() in cand_text or cand_text in text.lower():
                            ent_type = cand_type
                            break
                if not ent_type: continue
                
                allowed_types = event_schema[role]
                if ent_type not in allowed_types: continue
                
                arg["role"] = role
                valid_arguments.append(arg)

            return valid_arguments
        except Exception as e:
            print(f"  [Argument Extraction] Error on attempt {attempt + 1}: {e}")
    return []


# ----------------------------------------------------------------------
# 5. Post-Processing & Output Formulation
# ----------------------------------------------------------------------
def post_process_llm_output(llm_data, input_rec, token_spans, raw_response=None,
                             valid_entity_types=None, valid_event_types=None, valid_roles=None):
    sentence = input_rec["sentence"]
    doc_id = input_rec["doc_id"]
    sent_id = input_rec["sent_id"]

    used_char_spans = []

    # Deduplicate Entities
    extracted_entities = []
    seen_texts = set()
    for ent in llm_data.get("entities", []):
        if not isinstance(ent, dict): continue
        t = str(ent.get("text", "")).strip()
        tp = str(ent.get("type", "")).strip()
        if not t or not tp: continue
        if (t, tp) not in seen_texts:
            seen_texts.add((t, tp))
            extracted_entities.append({"text": t, "type": tp})

    entity_mentions = []
    entity_text_to_id = {}

    for idx, ent in enumerate(extracted_entities):
        text = ent["text"]
        full_type = ent["type"]

        valid_entity_types_lower = {t.lower(): t for t in valid_entity_types} if valid_entity_types else {}
        matched_type = valid_entity_types_lower.get(full_type.lower())
        entity_type = matched_type if matched_type is not None else full_type

        is_oov = not (valid_entity_types and entity_type in valid_entity_types)
        start_char, end_char = find_available_span(sentence, text, used_char_spans)
        
        is_valid_text = start_char != -1
        if not is_valid_text:
            start_char = end_char = start_token = end_token = 0
        else:
            used_char_spans.append((start_char, end_char))
            start_token, end_token = char_span_to_token_span(start_char, end_char, token_spans)

        ent_id = f"{sent_id}-T{idx + 1}"
        entity_mentions.append({
            "id": ent_id, "text": text, "entity_type": entity_type,
            "start": start_token, "end": end_token, "start_char": start_char, "end_char": end_char,
            "mention_type": "UNK", "is_oov": is_oov, "is_valid_text": is_valid_text
        })
        entity_text_to_id[text] = ent_id

    # Post-process Events
    event_mentions = []
    trigger_counter = len(entity_mentions) + 1

    for ev in llm_data.get("events", []):
        if not isinstance(ev, dict): continue
        
        trigger_text = str(ev.get("trigger", "") if not isinstance(ev.get("trigger"), dict) else ev.get("trigger").get("text", "")).strip()
        full_event_type = str(ev.get("type", "")).strip()
        if not trigger_text or not full_event_type: continue
        if sentence.find(trigger_text) == -1: continue

        valid_event_types_lower = {t.lower(): t for t in valid_event_types} if valid_event_types else {}
        matched_event = valid_event_types_lower.get(full_event_type.lower())
        event_type = matched_event if matched_event is not None else full_event_type

        is_oov_ev = not (valid_event_types and event_type in valid_event_types)
        start_char, end_char = find_available_span(sentence, trigger_text, used_char_spans)
        
        is_valid_ev_text = start_char != -1
        if not is_valid_ev_text:
            start_char = end_char = start_token = end_token = 0
        else:
            used_char_spans.append((start_char, end_char))
            start_token, end_token = char_span_to_token_span(start_char, end_char, token_spans)

        event_id = f"{sent_id}-T{trigger_counter}"
        trigger_counter += 1

        arguments = []
        for arg in ev.get("arguments", []):
            if not isinstance(arg, dict): continue
            arg_text = str(arg.get("text", "")).strip()
            full_role = str(arg.get("role", "")).strip()
            if not arg_text or not full_role: continue

            valid_roles_lower = {t.lower(): t for t in valid_roles} if valid_roles else {}
            matched_role = valid_roles_lower.get(full_role.lower())
            role = matched_role if matched_role is not None else full_role

            ent_id = entity_text_to_id.get(arg_text)
            if ent_id:
                arguments.append({
                    "entity_id": ent_id, "text": arg_text, "role": role,
                    "is_oov": not (valid_roles and role in valid_roles),
                    "is_valid_text": sentence.find(arg_text) != -1
                })

        event_mentions.append({
            "id": event_id, "event_type": event_type,
            "trigger": {"text": trigger_text, "start": start_token, "end": end_token, "start_char": start_char, "end_char": end_char},
            "arguments": arguments, "is_oov": is_oov_ev, "is_valid_text": is_valid_ev_text
        })

    referenced_entity_ids = {arg["entity_id"] for ev in event_mentions for arg in ev.get("arguments", [])}
    filtered_entity_mentions = [ent for ent in entity_mentions if ent["id"] in referenced_entity_ids]

    return {
        "doc_id": doc_id, "sent_id": sent_id, "tokens": input_rec["tokens"], "sentence": sentence,
        "entity_mentions": filtered_entity_mentions, "event_mentions": event_mentions,
        "relation_mentions": input_rec.get("relation_mentions", []), "raw_response": raw_response
    }


# ----------------------------------------------------------------------
# 6. Evaluation Logic (Placeholder for brevity, keep existing logic)
# ----------------------------------------------------------------------
# Note: Retain the existing `calculate_metrics`, `is_similar_text`, and 
# `evaluate_extracted_file` from your original extract_llm.py here.


# ----------------------------------------------------------------------
# 7. Processing Runner
# ----------------------------------------------------------------------
def process_single_record(task_args):
    idx, rec, entity_types, event_types, roles = task_args
    sentence = rec["sentence"]
    tokens = rec["tokens"]
    
    print(f"[{idx + 1}] Extracting medical events...")
    token_spans = compute_token_spans(sentence, tokens)

    entities = extract_entities_with_llm(sentence, entity_types)
    events_raw = extract_event_triggers_with_llm(sentence, event_types)

    valid_events_raw = []
    valid_event_types_lower = {t.lower(): t for t in event_types}
    for ev in events_raw:
        trigger = ev.get("trigger", "").strip()
        ev_type = ev.get("type", "").strip()
        if not trigger or not ev_type: continue
        matched_type = valid_event_types_lower.get(ev_type.lower())
        if matched_type:
            ev["type"] = matched_type
            valid_events_raw.append(ev)

    events = []
    for ev in valid_events_raw:
        trigger = ev.get("trigger", "")
        ev_type = ev.get("type", "")
        if not trigger or not ev_type: continue
        args = extract_event_arguments_with_llm(sentence, ev_type, trigger, entities, roles)
        events.append({"trigger": trigger, "type": ev_type, "arguments": args})

    processed_rec = post_process_llm_output(
        {"entities": entities, "events": events}, rec, token_spans,
        raw_response="Medical LLM Process Completed.",
        valid_entity_types=entity_types, valid_event_types=event_types, valid_roles=roles
    )
    return idx, processed_rec


# ----------------------------------------------------------------------
# 8. Main Execution
# ----------------------------------------------------------------------
def main():
    entity_types, event_types, roles = get_types_from_schema()
    if not entity_types or not event_types:
        print("Dynamic type extraction failed.")
        return

    input_records = []
    try:
        import gzip
        open_func = gzip.open if INPUT_FILE.endswith(".gz") else open
        mode = "rt" if INPUT_FILE.endswith(".gz") else "r"
        with open_func(INPUT_FILE, mode, encoding="utf-8") as f:
            for line in f:
                if line.strip(): input_records.append(json.loads(line.strip()))
    except FileNotFoundError:
        print(f"Error: {INPUT_FILE} not found.")
        return

    if MAX_SAMPLES and MAX_SAMPLES < len(input_records):
        input_records = input_records[:MAX_SAMPLES]

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    
    tasks = [(idx, rec, entity_types, event_types, roles) for idx, rec in enumerate(input_records)]
    
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(process_single_record, task) for task in tasks]
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
            for future in futures:
                idx, rec = future.result()
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                out.flush()
                print(f"[{idx + 1}/{len(input_records)}] Saved to {OUTPUT_FILE}")

    print(f"\nMedical extraction completed -> {OUTPUT_FILE}")

if __name__ == "__main__":
    main()