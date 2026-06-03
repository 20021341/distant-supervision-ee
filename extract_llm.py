import datetime
import json
import os
import re
import difflib
from collections import defaultdict
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
# Support both train.json.gz and train.json fallback
INPUT_FILE = "final_data/processed_enriched_3/train.json.gz"
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = "final_data/processed_enriched_3/train.json"

MAX_SAMPLES = 50  # Set to None to run all sentences in the file
NUM_THREADS = 8   # Number of concurrent threads for LLM processing
TEMPERATURE = 0.0  # Set to 0.0 for deterministic/consistent results

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

# Dynamic unique output filename for V6
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
OUTPUT_FILE = f"final_data/processed_enriched_3/train_llm_extracted_v6_{timestamp}.json"


# ----------------------------------------------------------------------
# 1. Load Dynamic Schema from schema.json
# ----------------------------------------------------------------------
with open("schema.json", "r", encoding="utf-8") as f:
    SCHEMA_DATA = json.load(f)

# ----------------------------------------------------------------------
# 2. Type Definition Descriptions (Natural Language Explanations)
# ----------------------------------------------------------------------
ENTITY_TYPE_DESCRIPTIONS = {
    "Person": "A human being, referenced individually or collectively (e.g., civilian, soldier, president, they).",
    "Organization": "A formal association of people, such as government agencies, companies, clubs, political parties, or military groups.",
    "Geopolitical-Entity": "A geographical area with an associated government, such as countries, cities, provinces, states, or regions.",
    "Location": "A geographical location, place, body of water, or natural landmark that is not a geopolitical entity.",
    "Facility": "A human-made functional building or structure, such as a bridge, airport, building, room, or highway.",
    "Weapon": "An instrument or device designed or used for inflicting physical bodily harm or damage (e.g., gun, bomb, knife).",
    "Vehicle": "A physical device or machine designed for transporting people or goods (e.g., ship, plane, train, car).",
    "Time": "A specific point in time, date, duration, year, or frequency (e.g., yesterday, 14h, 2026, monthly).",
    "Crime": "A specific law violation, charge, offense, or illegal act (e.g., theft, corruption, disobeying court order).",
    "Job": "A professional title, position, occupation, or role in an organization (e.g., president, police chief, farmer).",
    "Sentence": "A legal punishment or penalty handed down by a court of law (e.g., 5 years in prison, death penalty).",
    "Money": "A monetary amount, currency, or financial value (e.g., 975 million USD, 13,300 billion VND).",
    "Number": "A numerical value or percentage (e.g., 10, 14%, 3.850 tons)."
}

EVENT_TYPE_DESCRIPTIONS = {
    "Life:Be-Born": "A person is born.",
    "Life:Marry": "Two persons are legally united in marriage.",
    "Life:Divorce": "Two spouses are legally divorced.",
    "Life:Injure": "A person suffers physical injury due to an accident or action.",
    "Life:Die": "A person dies due to a specific event or action.",
    "Movement:Transport": "Movement of people, weapons, vehicles, or artifacts from one place to another.",
    "Transaction:Transfer-Ownership": "Buying, selling, or transferring the legal ownership of an asset, organization, or physical object.",
    "Transaction:Transfer-Money": "Giving, receiving, or transferring money, funds, or financial capital between parties.",
    "Business:Start-Organization": "Creating, establishing, or launching a new organization or business entity.",
    "Business:Merge-Organization": "Two or more organizations combine into a single entity.",
    "Business:Declare-Bankruptcy": "An organization or individual legally declares bankruptcy.",
    "Business:End-Organization": "An organization or business is dissolved, shut down, or terminated.",
    "Conflict:Attack": "A violent physical act or assault aimed at causing harm, injury, or damage.",
    "Conflict:Demonstrate": "A public gathering, protest, rally, or political demonstration.",
    "Contact:Meet": "A face-to-face meeting, assembly, or physical gathering of people or representatives.",
    "Contact:Phone-Write": "Communication between two or more parties via phone calls, letters, emails, or written messages.",
    "Personnel:Start-Position": "A person starts a new job, position, or official title within an organization.",
    "Personnel:End-Position": "A person leaves, resigns, or is terminated from a job, position, or official title.",
    "Personnel:Nominate": "A person is officially nominated or proposed for a position or title.",
    "Personnel:Elect": "A person is officially elected to a position, office, or political title.",
    "Justice:Arrest-Jail": "A person is arrested, detained, or imprisoned by law enforcement.",
    "Justice:Release-Parole": "A person is released from jail, prison, custody, or placed on parole.",
    "Justice:Trial-Hearing": "A formal court trial, hearing, or legal proceeding.",
    "Justice:Charge-Indict": "A person or organization is formally charged or indicted for a crime.",
    "Justice:Sue": "A person or entity files a civil lawsuit against another.",
    "Justice:Convict": "A defendant is officially found guilty of a crime by a court.",
    "Justice:Sentence": "A defendant is officially sentenced to a punishment or penalty.",
    "Justice:Fine": "A defendant is ordered to pay a financial fine as punishment.",
    "Justice:Execute": "A person is executed as legal capital punishment.",
    "Justice:Extradite": "A person is extradited from one country/jurisdiction to another.",
    "Justice:Acquit": "A defendant is officially declared not guilty or acquitted of charges.",
    "Justice:Pardon": "A person is officially pardoned and cleared of criminal conviction.",
    "Justice:Appeal": "An appeal is submitted against a court decision."
}

ROLE_DESCRIPTIONS = {
    "Place": "The location where the event occurs.",
    "Time": "The time or date when the event occurs.",
    "Person": "The person participating in or affected by the event.",
    "Agent": "The active entity, person, or organization that instigates or performs the event.",
    "Victim": "The person who is harmed, injured, or killed in the event.",
    "Instrument": "The weapon, device, or vehicle used to carry out the event.",
    "Artifact": "The physical object, weapon, vehicle, or organization being transported or transferred.",
    "Vehicle": "The vehicle used for transportation.",
    "Price": "The monetary amount or cost of a transaction or transport.",
    "Origin": "The starting point or source location of a movement or transport.",
    "Destination": "The ending point or target location of a movement or transport.",
    "Buyer": "The entity or person purchasing an asset or organization.",
    "Seller": "The entity or person selling an asset or organization.",
    "Beneficiary": "The entity or person that benefits from a transaction or transfer.",
    "Giver": "The entity or person sending or donating money or capital.",
    "Recipient": "The entity or person receiving money or capital.",
    "Money": "The money or currency amount involved in a transaction.",
    "Organization": "The organization that is started, ended, merged, or affected by the event.",
    "Attacker": "The person, group, or nation initiating a violent attack.",
    "Target": "The person, organization, vehicle, facility, or location targeted by an attack.",
    "Entity": "The participant(s) or communicator(s) in a meeting, phone call, or demonstration.",
    "Position": "The job title, office, or official position concerned.",
    "Defendant": "The accused person or organization in a legal or justice proceeding.",
    "Prosecutor": "The authority, lawyer, or state entity prosecuting the defendant.",
    "Adjudicator": "The judge, jury, court, or legal authority making a decision.",
    "Crime": "The specific crime, offense, or charge being tried, arrested for, or committed.",
    "Sentence": "The specific legal penalty or prison sentence handed down by a court.",
    "Plaintiff": "The person or entity bringing a civil lawsuit against a defendant."
}


# ----------------------------------------------------------------------
# 3. Dynamic Type Aggregation
# ----------------------------------------------------------------------
def get_types_from_schema():
    print("Loading valid types directly from schema.json...")
    entity_types = SCHEMA_DATA.get("entities", [])
    roles = SCHEMA_DATA.get("arguments", [])
    event_types = list(SCHEMA_DATA.get("events", {}).keys())
    print(f"Loaded {len(entity_types)} entity types, {len(event_types)} event types, and {len(roles)} argument roles strictly from Schema.")
    return sorted(entity_types), sorted(event_types), sorted(roles)


# ----------------------------------------------------------------------
# 4. Token Matching & Span Computation
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
# 5. LLM Prompt Templates (V6) — Descriptions, Strict Standard Labels
# ----------------------------------------------------------------------

FEW_SHOT_ENTITIES = """\
Example 1:
Input Sentence: "Ngày 26/11 , Bộ Tài chính khai trương giao diện mới Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước ."
Output JSON:
{
  "thought": "Let's identify all valid entity mentions in the sentence. First, 'Ngày 26/11' is a date, which fits the 'Time' category. Next, 'Bộ Tài chính' is a government entity, which is an 'Organization'. The phrase 'Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước' is a formal digital government entity, so it is an 'Organization'. We will extract these three distinct entities.",
  "entities": [
    {"text": "Ngày 26/11", "type": "Time"},
    {"text": "Bộ Tài chính", "type": "Organization"},
    {"text": "Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước", "type": "Organization"}
  ]
}

Example 2:
Input Sentence: "Tòa án đã tuyên án 5 năm tù đối với bị can Nguyễn Văn A vì tội tham ô tài sản công ."
Output JSON:
{
  "thought": "Let's identify all valid entity mentions. 'Tòa án' (court) is a judicial body, fitting 'Organization'. '5 năm tù' represents a court-ordered legal penalty, which fits 'Sentence'. 'bị can Nguyễn Văn A' is a specific person referred to in a legal case; the whole phrase 'bị can Nguyễn Văn A' (or the pronoun/title 'bị can' and 'Nguyễn Văn A') represents a human being, so we extract 'bị can Nguyễn Văn A' as 'Person'. 'tham ô' represents a specific illegal act or violation of law, which fits 'Crime'. We will extract all of these.",
  "entities": [
    {"text": "Tòa án", "type": "Organization"},
    {"text": "5 năm tù", "type": "Sentence"},
    {"text": "bị can Nguyễn Văn A", "type": "Person"},
    {"text": "tham ô", "type": "Crime"}
  ]
}

Example 3:
Input Sentence: "Ông Hưng dùng súng bắn vào nhóm người đang đứng trước nhà riêng của ông ở Hà Nội ."
Output JSON:
{
  "thought": "Let's identify all valid entities. 'Ông Hưng' is a specific person, so we extract it as 'Person'. 'súng' (gun) is a physical weapon, fitting 'Weapon'. 'nhóm người' is a collection of people, which fits 'Person' collectively. 'nhà riêng' is a functional building, fitting 'Facility'. The pronoun 'ông' refers back to 'Ông Hưng' and is a valid 'Person' reference. 'Hà Nội' is a major city/GPE, so it is 'Geopolitical-Entity'. We must comprehensively extract all of them, including pronouns like 'ông'.",
  "entities": [
    {"text": "Ông Hưng", "type": "Person"},
    {"text": "súng", "type": "Weapon"},
    {"text": "nhóm người", "type": "Person"},
    {"text": "nhà riêng", "type": "Facility"},
    {"text": "ông", "type": "Person"},
    {"text": "Hà Nội", "type": "Geopolitical-Entity"}
  ]
}

Example 4:
Input Sentence: "Ít nhất 10 người đã thiệt mạng và hàng chục người nhập viện trong các vụ bạo lực ở Thái Lan ."
Output JSON:
{
  "thought": "CRITICAL: When a sentence contains quantified person groups (e.g. '10 người', 'hàng chục người'), EACH group is a separate Person entity even if they appear in the same sentence. '10 người' is the group who died → Person. 'hàng chục người' is the group who were hospitalized → Person. 'Thái Lan' is a country → Geopolitical-Entity. Do NOT collapse all person mentions into one.",
  "entities": [
    {"text": "10 người", "type": "Person"},
    {"text": "hàng chục người", "type": "Person"},
    {"text": "Thái Lan", "type": "Geopolitical-Entity"}
  ]
}

Example 5:
Input Sentence: "Chiều 1/5 , Phong mang theo nhiều dây chuyền , nhẫn vàng đến một tiệm vàng S. nằm trên địa bàn thị xã Ayun Pa , tỉnh Gia Lai để bán ."
Output JSON:
{
  "thought": "Let's identify all entities. 'Chiều 1/5' is a specific time → Time. 'Phong' is a person's name → Person. VALUABLE GOODS RULE: 'nhiều dây chuyền , nhẫn vàng' (many necklaces, gold rings) are valuable goods with monetary/tradeable value being transported to be sold → Money. 'tiệm vàng S.' is a commercial shop/store → Location (a non-GPE place, not an Organization). 'thị xã Ayun Pa' is an administrative region → Geopolitical-Entity.",
  "entities": [
    {"text": "Chiều 1/5", "type": "Time"},
    {"text": "Phong", "type": "Person"},
    {"text": "nhiều dây chuyền , nhẫn vàng", "type": "Money"},
    {"text": "tiệm vàng S.", "type": "Location"},
    {"text": "thị xã Ayun Pa", "type": "Geopolitical-Entity"}
  ]
}

Example 6:
Input Sentence: "Ông Hưng nổ nhiều phát súng tại quán ăn đêm , sau đó các đối tác nước ngoài đã huỷ hợp đồng ."
Output JSON:
{
  "thought": "Let's identify all entities. 'Ông Hưng' is a specific person → Person. WEAPON RULE: The phrase 'nổ nhiều phát súng' (fired multiple shots) contains a weapon noun 'súng' (gun). Even though 'súng' is embedded in the action phrase, I MUST extract it as Weapon. 'quán ăn đêm' (late-night restaurant) is a named facility → Facility. COLLECTIVE REFERENCE RULE: 'các đối tác nước ngoài' (the foreign partners) — 'các đối tác' is a collective noun phrase referring to multiple partner organizations → Organization.",
  "entities": [
    {"text": "Ông Hưng", "type": "Person"},
    {"text": "súng", "type": "Weapon"},
    {"text": "quán ăn đêm", "type": "Facility"},
    {"text": "các đối tác nước ngoài", "type": "Organization"}
  ]
}
"""

FEW_SHOT_TRIGGERS = """\
Example 1:
Input Sentence: "Ngày 26/11 , Bộ Tài chính khai trương giao diện mới Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước ."
Output JSON:
{
  "thought": "I need to identify all keywords or phrases signaling a valid event. The action 'khai trương' (launch/inaugurate) represents the establishment of a new entity ('Cổng thông tin điện tử'), so it triggers 'Business:Start-Organization'. I will extract it.",
  "events": [
    {"trigger": "khai trương", "type": "Business:Start-Organization"}
  ]
}

Example 2:
Input Sentence: "Ít nhất 10 người đã thiệt mạng và hàng chục người nhập viện trong các vụ bạo lực ở Thái Lan ."
Output JSON:
{
  "thought": "Let's find all event signals. 1) 'thiệt mạng' (perish/die) signals 'Life:Die'. 2) 'nhập viện' (hospitalized) implies people suffered physical harm, triggering 'Life:Injure'. 3) 'bạo lực' (violence) represents violent public clashes or civil unrest, triggering 'Conflict:Demonstrate'. I will extract all three triggers to ensure high recall.",
  "events": [
    {"trigger": "thiệt mạng", "type": "Life:Die"},
    {"trigger": "nhập viện", "type": "Life:Injure"},
    {"trigger": "bạo lực", "type": "Conflict:Demonstrate"}
  ]
}

Example 3:
Input Sentence: "Chính phủ quyết định điều động quân đội đến hỗ trợ vùng lũ lụt , đồng thời hỗ trợ 50 tỷ đồng cho người dân ."
Output JSON:
{
  "thought": "Let's look for event triggers. 'điều động' (mobilize/transfer) indicates the movement of soldiers, triggering 'Movement:Transport'. 'hỗ trợ' (support/give money) involving '50 tỷ đồng' represents a transfer of financial capital, triggering 'Transaction:Transfer-Money'. I will extract both.",
  "events": [
    {"trigger": "điều động", "type": "Movement:Transport"},
    {"trigger": "hỗ trợ", "type": "Transaction:Transfer-Money"}
  ]
}

Example 4:
Input Sentence: "Ông Hưng nổ nhiều phát súng tại quán ăn đêm , làm bị thương nhiều người ."
Output JSON:
{
  "thought": "CRITICAL: The full action phrase 'nổ nhiều phát súng' (firing multiple gunshots) is the complete trigger for a Conflict:Attack event. Do NOT truncate it to just 'nổ' (explode) — extract the full verb phrase that describes the violent act. 'làm bị thương' (causing injury) is a result clause, but it implies physical injury, triggering 'Life:Injure'.",
  "events": [
    {"trigger": "nổ nhiều phát súng", "type": "Conflict:Attack"},
    {"trigger": "bị thương", "type": "Life:Injure"}
  ]
}

Example 5:
Input Sentence: "Toà án tuyên phạt tử hình bị cáo Nguyễn Văn B vì tội giết người ."
Output JSON:
{
  "thought": "CRITICAL TYPE DISTINCTION: 'tử hình' (death penalty/execution) when administered by a court as a legal sentence is 'Justice:Execute' (legal capital punishment), NOT 'Life:Die'. The verb 'tuyên phạt' (to sentence/convict) alongside 'tử hình' signals a judicial execution event. Extract 'tử hình' as 'Justice:Execute'.",
  "events": [
    {"trigger": "tử hình", "type": "Justice:Execute"}
  ]
}
"""

FEW_SHOT_ARGUMENTS = """\
Example 1:
Sentence: "Ngày 26/11 , Bộ Tài chính khai trương giao diện mới Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước ."
Event Type: "Business:Start-Organization"
Event Trigger: "khai trương"
Candidate Entities: [{"text": "Ngày 26/11", "type": "Time"}, {"text": "Bộ Tài chính", "type": "Organization"}, {"text": "Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước", "type": "Organization"}]
Output JSON:
{
  "thought": "The event is 'Business:Start-Organization' triggered by 'khai trương'. I must check DIRECT grammatical/semantic connection to the trigger for each candidate. 1) 'Bộ Tài chính' is the grammatical SUBJECT of 'khai trương' → Agent (direct link). 2) 'Cổng thông tin điện tử...' is the grammatical OBJECT of 'khai trương' → Organization (direct link). 3) 'Ngày 26/11' is a temporal adverbial directly modifying the event → Time (direct link). 4) Place: no location phrase directly modifies 'khai trương' → skip.",
  "arguments": [
    {"text": "Bộ Tài chính", "role": "Agent"},
    {"text": "Ngày 26/11", "role": "Time"},
    {"text": "Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước", "role": "Organization"}
  ]
}

Example 2:
Sentence: "Ít nhất 10 người đã thiệt mạng và hàng chục người nhập viện trong các vụ bạo lực ở Thái Lan ."
Event Type: "Life:Die"
Event Trigger: "thiệt mạng"
Candidate Entities: [{"text": "10 người", "type": "Person"}, {"text": "hàng chục người", "type": "Person"}, {"text": "Thái Lan", "type": "Geopolitical-Entity"}]
Output JSON:
{
  "thought": "The event is 'Life:Die' triggered by 'thiệt mạng'. I check each candidate's DIRECT link to this specific trigger. 1) '10 người' is the grammatical subject of 'thiệt mạng' → Victim (direct link). 2) 'hàng chục người' is the subject of 'nhập viện', NOT 'thiệt mạng' → REJECT (belongs to a different event). 3) 'Thái Lan': the phrase 'ở Thái Lan' modifies 'bạo lực', NOT directly 'thiệt mạng'. The gold standard for this event does NOT assign Place to this trigger → REJECT. Only 1 argument is directly linked.",
  "arguments": [
    {"text": "10 người", "role": "Victim"}
  ]
}

Example 3:
Sentence: "Dẫn kinh nghiệm các nước , ông cho hay , họ thừa nhận việc dùng tiền thuế đóng góp của dân vào giải cứu ngân hàng , nhưng có phương án phục hồi rõ ràng ."
Event Type: "Transaction:Transfer-Money"
Event Trigger: "đóng góp"
Candidate Entities: [{"text": "ông", "type": "Person"}, {"text": "họ", "type": "Person"}, {"text": "dân", "type": "Person"}, {"text": "ngân hàng", "type": "Organization"}]
Output JSON:
{
  "thought": "The event is 'Transaction:Transfer-Money' triggered by 'đóng góp' (contribute). I check DIRECT grammatical/semantic links. 1) 'dân' appears in 'đóng góp của dân' — 'dân' is the possessor/agent of 'đóng góp' → Giver (direct link). 2) 'ngân hàng': 'giải cứu ngân hàng' is a PURPOSE clause, not a direct argument of 'đóng góp'. The money goes INTO 'giải cứu ngân hàng' as a purpose, but 'ngân hàng' is NOT the direct Recipient of the contribution → REJECT. 3) 'ông' and 'họ' are subjects of 'cho hay' and 'thừa nhận' respectively — they do not directly participate in the 'đóng góp' event → REJECT. Only 1 argument.",
  "arguments": [
    {"text": "dân", "role": "Giver"}
  ]
}
"""


def _parse_llm_json(raw_response):
    """Robustly parse JSON from LLM response, handling markdown code blocks."""
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
# 6. V6 LLM Extraction Functions
# ----------------------------------------------------------------------

def extract_entities_with_llm(sentence, entity_types):
    valid_entity_types_str = ""
    for et in entity_types:
        desc = ENTITY_TYPE_DESCRIPTIONS.get(et, "No description available.")
        valid_entity_types_str += f"- **{et}**: {desc}\n"

    system_prompt = f"""You are a comprehensive and precise Named Entity Recognition (NER) AI for Vietnamese text.
Your task is to identify and extract ALL entity mentions from the given Vietnamese sentence.

VALID ENTITY TYPES WITH DEFINITIONS:
{valid_entity_types_str}

EXTRACTION RULES:
1. Extract each entity text span EXACTLY as it appears in the sentence — do not modify, stem, or translate it.
2. Assign ONLY types from the VALID ENTITY TYPES list above. Use the exact spelling and capitalization of the label.
3. BE COMPREHENSIVE AND MAXIMIZE RECALL: Ensure you extract ALL entity mentions. 
   - CRITICAL: Pronouns and common noun references (such as 'ông', 'bà', 'anh', 'họ', 'ta', 'người', 'dân', 'nạn nhân', 'bị can', 'phạm nhân', 'cầu thủ', 'nông dân', 'tài xế', 'hành khách', 'công an', 'cảnh sát', 'chủ tiệm') are valid 'Person' mentions if they refer to specific human actors in the sentence. You MUST extract them.
   - Common organization terms like 'toà' (court), 'công ty' (company), 'ngân hàng' (bank), 'đại sứ quán' (embassy) are valid 'Organization' mentions.
   - Generic time expressions, dates, specific numeric quantities, money amounts, crime names, job roles, and sentences must also be comprehensively extracted.
   - Do NOT over-filter. It is better to extract a potential entity mention than to omit it.
   - WEAPON RULE: If a weapon noun (súng/gun, dao/knife, bom/bomb, lựu đạn/grenade, vũ khí/weapon, etc.) appears anywhere in the sentence — even embedded inside a verb phrase like 'nổ súng', 'cầm dao', 'ném bom', 'dùng súng bắn' — you MUST extract the weapon noun as a 'Weapon' entity. Do NOT skip weapons.
   - COLLECTIVE REFERENCE RULE: Phrases like 'các đối tác này', 'các công ty đó', 'những tổ chức trên' where 'các/những' precedes a collective noun are valid Organization or Person entities. Extract them with their FULL noun phrase including 'các/những'.
   - VALUABLE GOODS AS MONEY: Items explicitly described as having monetary/tradeable value — gold jewelry (dây chuyền vàng, nhẫn vàng, vàng miếng), foreign currency, valuable assets being sold or transferred — should be classified as 'Money' if they represent the monetary value of a transaction.
4. CRITICAL: Write a highly detailed "thought" in English BEFORE listing entities. Analyze the sentence word-by-word. Identify every possible noun phrase, pronoun, date, number, or crime. Compare each against the definitions and explicitly justify why they should be extracted to maximize coverage.
5. If no entities are found, return an empty list.

OUTPUT FORMAT (strict JSON only):
{{
  "thought": "Step-by-step English reasoning about all potential entities in the sentence to maximize recall",
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
            raw_response = response.choices[0].message.content
            parsed_json = _parse_llm_json(raw_response)
            return parsed_json.get("entities", [])
        except Exception as e:
            print(f"  [Entity Extraction] Error on attempt {attempt + 1}: {e}")
    return []


def extract_event_triggers_with_llm(sentence, event_types):
    valid_event_types_str = ""
    for evt in event_types:
        desc = EVENT_TYPE_DESCRIPTIONS.get(evt, "No description available.")
        valid_event_types_str += f"- **{evt}**: {desc}\n"

    system_prompt = f"""You are a comprehensive and highly responsive Event Detection AI for Vietnamese text.
Your task is to identify and extract ALL event triggers from the given Vietnamese sentence.

VALID EVENT TYPES WITH DEFINITIONS:
{valid_event_types_str}

EXTRACTION RULES:
1. Extract the shortest keyword, verb, or action noun phrase that DIRECTLY signals an event of a valid type.
2. The trigger must be an actual word or phrase found verbatim in the sentence.
3. Assign ONLY types from the VALID EVENT TYPES list above. Use the exact spelling and capitalization of the label.
4. BE COMPREHENSIVE AND MAXIMIZE RECALL: Ensure you capture ALL valid event triggers. Do NOT over-filter. It is better to extract a potential event trigger than to miss it.
   - CRITICAL (Short Movement Verbs): Extract common verbs of physical movement like 'đến', 'đi vào', 'tới', 'đi', 'rút', 'di chuyển' as 'Movement:Transport' triggers when they signify people, weapons, vehicles, or artifacts moving. Do not miss them!
   - CRITICAL (Passive/State-based Financial Terms): Extract financial states or passive transactions such as 'nợ' (owing/debt), 'vay' (borrowing), 'mang' (carrying assets for a transaction), 'tiền thuế', 'nộp' or 'đóng góp' (paying/submitting tax/fee/contribution) as 'Transaction:Transfer-Money' triggers.
   - CRITICAL (Nominal/Metaphorical Deaths and Dissolutions): Extract nominal actions that imply death like 'tự sát' (suicide) or 'tội chết' (death penalty) as 'Life:Die' triggers. Extract metaphorical or indirect organizational closures like 'đào thải' (elimination/weeding out) as 'Business:End-Organization' triggers.
5. CRITICAL: Write a highly detailed "thought" in English BEFORE listing events. Analyze the verbs, action nouns, and states in the sentence. Compare each against the event definitions and explicitly justify why they should be extracted to maximize coverage.
6. If no events are found, return an empty list.

OUTPUT FORMAT (strict JSON only):
{{
  "thought": "Step-by-step English reasoning about all event signals in the sentence to maximize recall",
  "events": [
    {{"trigger": "exact trigger word from sentence", "type": "exact event type from valid list"}}
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
            raw_response = response.choices[0].message.content
            parsed_json = _parse_llm_json(raw_response)
            return parsed_json.get("events", [])
        except Exception as e:
            print(f"  [Trigger Extraction] Error on attempt {attempt + 1}: {e}")
    return []


def extract_event_arguments_with_llm(sentence, event_type, trigger, entities, roles):
    # Load dynamic role schema constraint from schema.json
    event_schema = SCHEMA_DATA["events"].get(event_type, {}).get("schema", {})
    allowed_roles = list(event_schema.keys())

    valid_roles_str = ""
    for r in allowed_roles:
        desc = ROLE_DESCRIPTIONS.get(r, "No description available.")
        valid_roles_str += f"- **{r}**: {desc}\n"
    
    # Format the strict schema hint for the LLM
    role_schema_hint = f"For the '{event_type}' event, the allowed argument roles and the entity types that can fill them are:\n"
    for r, allowed_ents in event_schema.items():
        role_schema_hint += f"  - **{r}** (Can only be filled by: {', '.join(allowed_ents)})\n"

    system_prompt = f"""You are a highly precise Event Argument Extraction AI for Vietnamese text.
Given a Vietnamese sentence with an identified event, select ONLY the candidate entities that DIRECTLY fill the argument roles of THAT SPECIFIC event trigger.

SENTENCE: "{sentence}"
EVENT TYPE: "{event_type}"
EVENT TRIGGER: "{trigger}"
CANDIDATE ENTITIES WITH TYPES: {json.dumps(entities, ensure_ascii=False)}

EVENT SCHEMAS (ALLOWED ROLES AND ACCEPTABLE ENTITY TYPES):
{role_schema_hint}

VALID ARGUMENT ROLES WITH DEFINITIONS:
{valid_roles_str}

CRITICAL RULES — READ CAREFULLY:
1. **DIRECT-LINK PRINCIPLE**: An entity MUST have a DIRECT grammatical or semantic connection to the trigger word "{trigger}" to be assigned a role. The entity must be a grammatical subject, object, adverbial modifier, or prepositional complement that directly governs or is governed by the trigger.
2. **REJECT entities that belong to a DIFFERENT event/clause**: If a sentence contains multiple events, an entity that is the subject/object of a DIFFERENT verb or trigger should NOT be assigned to THIS event. Each event trigger "owns" only its own grammatical arguments.
3. **REJECT distant/indirect connections**: Do NOT assign roles based on world knowledge, inference, or contextual background. If an entity is connected to the trigger only through a PURPOSE clause (e.g., "để...", "vào...", "cho..."), a RELATIVE clause, or a separate main clause, it is NOT a direct argument — REJECT it.
4. **REJECT Time/Place over-assignment**: Only assign Time or Place if the time/location phrase DIRECTLY and IMMEDIATELY modifies THIS specific trigger, not a parent clause or a different event in the same sentence.
5. Assign each selected entity exactly ONE valid role from the VALID ARGUMENT ROLES list.
6. Ensure the selected entity's type is strictly allowed for the assigned role per the EVENT SCHEMAS.
7. If NO candidate satisfies a role with a DIRECT link, leave that role EMPTY. It is better to leave a role unfilled than to assign an incorrect entity.
8. CRITICAL: Write a highly detailed "thought" in English BEFORE extracting arguments. For EACH allowed role:
   - Identify which candidate(s) could fill it.
   - Explicitly state the GRAMMATICAL relationship between the candidate and the trigger (e.g., "X is the subject of verb Y", "X is a prepositional object of 'tại' which modifies Y").
   - If the relationship is indirect, explicitly state "REJECT — indirect link" and explain why.

OUTPUT FORMAT (strict JSON only):
{{
  "thought": "Step-by-step role analysis with explicit grammatical justification for each role",
  "arguments": [
    {{"text": "exact text matching a candidate entity", "role": "exact role from valid list"}}
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
                    {"role": "user", "content": f'Assign argument roles for "{event_type}" event triggered by "{trigger}":\nOutput JSON:'}
                ],
                response_format={"type": "json_object"},
                temperature=TEMPERATURE
            )
            raw_response = response.choices[0].message.content
            parsed_json = _parse_llm_json(raw_response)
            raw_arguments = parsed_json.get("arguments", [])

            # === Step 3: Schema Validation Filter ===
            valid_arguments = []
            entity_type_map = {ent["text"].lower().strip(): ent["type"] for ent in entities}
            
            for arg in raw_arguments:
                text = arg.get("text", "").strip()
                role = arg.get("role", "").strip()
                if not text or not role:
                    continue
                
                # 1. Verify if the role is allowed in schema for this event type
                if role not in event_schema:
                    # Try a case-insensitive match for the role
                    matched_role = None
                    for schema_role in event_schema.keys():
                        if schema_role.lower() == role.lower():
                            matched_role = schema_role
                            break
                    if matched_role:
                        role = matched_role
                    else:
                        print(f"   [Schema Filter] Dropping argument role '{role}' — not valid for event type '{event_type}'.")
                        continue
                
                # 2. Get the entity type of the selected text
                ent_type = entity_type_map.get(text.lower())
                if not ent_type:
                    # Soft match
                    for cand_text, cand_type in entity_type_map.items():
                        if text.lower() in cand_text or cand_text in text.lower():
                            ent_type = cand_type
                            break
                
                if not ent_type:
                    print(f"   [Schema Filter] Dropping argument '{text}' — could not resolve to a candidate entity.")
                    continue
                
                # 3. Verify if the entity type is allowed for this role
                allowed_types = event_schema[role]
                if ent_type not in allowed_types:
                    print(f"   [Schema Filter] Dropping argument '{text}' (Type: {ent_type}) for role '{role}' — incompatible type. Allowed: {allowed_types}")
                    continue
                
                # Update argument with sanitized/validated info
                arg["role"] = role
                valid_arguments.append(arg)

            return valid_arguments
        except Exception as e:
            print(f"  [Argument Extraction] Error on attempt {attempt + 1}: {e}")
    return []


# ----------------------------------------------------------------------
# 7. Post-Processing & Output Formulation
# ----------------------------------------------------------------------
def post_process_llm_output(llm_data, input_rec, token_spans, raw_response=None,
                             valid_entity_types=None, valid_event_types=None, valid_roles=None):
    sentence = input_rec["sentence"]
    doc_id = input_rec["doc_id"]
    sent_id = input_rec["sent_id"]

    used_char_spans = []

    # Deduplicate extracted entities
    extracted_entities = []
    seen_texts = set()
    for ent in llm_data.get("entities", []):
        if isinstance(ent, str):
            ent = {"text": ent, "type": "UNK"}
        elif not isinstance(ent, dict):
            continue

        t = ent.get("text", "")
        if not isinstance(t, str):
            t = str(t)
        t = t.strip()

        tp = ent.get("type", "")
        if not isinstance(tp, str):
            tp = str(tp)
        tp = tp.strip()

        if not t or not tp:
            continue
        if (t, tp) not in seen_texts:
            seen_texts.add((t, tp))
            extracted_entities.append({"text": t, "type": tp})

    entity_mentions = []
    entity_text_to_id = {}

    for idx, ent in enumerate(extracted_entities):
        text = ent["text"]
        full_type = ent["type"]

        # Case-insensitive robust mapping back to valid entity type casing
        valid_entity_types_lower = {t.lower(): t for t in valid_entity_types} if valid_entity_types else {}
        matched_type = valid_entity_types_lower.get(full_type.lower())
        entity_type = matched_type if matched_type is not None else full_type

        is_oov = not (valid_entity_types and entity_type in valid_entity_types)

        start_char, end_char = find_available_span(sentence, text, used_char_spans)
        is_valid_text = True
        if start_char == -1:
            is_valid_text = False
            start_char = 0
            end_char = 0
            start_token = 0
            end_token = 0
        else:
            used_char_spans.append((start_char, end_char))
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
        if not isinstance(ev, dict):
            continue
        trigger_text = ev.get("trigger", "")
        if isinstance(trigger_text, dict):
            trigger_text = trigger_text.get("text", "")
        if not isinstance(trigger_text, str):
            trigger_text = str(trigger_text)
        trigger_text = trigger_text.strip()

        full_event_type = ev.get("type", "")
        if not isinstance(full_event_type, str):
            full_event_type = str(full_event_type)
        full_event_type = full_event_type.strip()

        if not trigger_text or not full_event_type:
            continue

        # Soft filter: skip triggers that don't actually appear in the sentence
        if sentence.find(trigger_text) == -1:
            print(f"   [Post-process] Dropping trigger '{trigger_text}' — not found in sentence.")
            continue

        # Case-insensitive event type mapping
        valid_event_types_lower = {t.lower(): t for t in valid_event_types} if valid_event_types else {}
        matched_event = valid_event_types_lower.get(full_event_type.lower())
        event_type = matched_event if matched_event is not None else full_event_type

        is_oov_ev = not (valid_event_types and event_type in valid_event_types)

        start_char, end_char = find_available_span(sentence, trigger_text, used_char_spans)
        is_valid_ev_text = True
        if start_char == -1:
            is_valid_ev_text = False
            start_char = 0
            end_char = 0
            start_token = 0
            end_token = 0
        else:
            used_char_spans.append((start_char, end_char))
            start_token, end_token = char_span_to_token_span(start_char, end_char, token_spans)

        event_id = f"{sent_id}-T{trigger_counter}"
        trigger_counter += 1

        arguments = []
        for arg in ev.get("arguments", []):
            if not isinstance(arg, dict):
                continue
            arg_text = arg.get("text", "")
            if not isinstance(arg_text, str):
                arg_text = str(arg_text)
            arg_text = arg_text.strip()

            full_role = arg.get("role", "")
            if not isinstance(full_role, str):
                full_role = str(full_role)
            full_role = full_role.strip()

            if not arg_text or not full_role:
                continue

            # Case-insensitive role mapping
            valid_roles_lower = {t.lower(): t for t in valid_roles} if valid_roles else {}
            matched_role = valid_roles_lower.get(full_role.lower())
            role = matched_role if matched_role is not None else full_role

            is_oov_arg = not (valid_roles and role in valid_roles)
            is_valid_arg_text = (sentence.find(arg_text) != -1)

            ent_id = entity_text_to_id.get(arg_text)

            if ent_id is None:
                arg_sc, arg_ec = find_available_span(sentence, arg_text, used_char_spans)
                if arg_sc != -1:
                    used_char_spans.append((arg_sc, arg_ec))
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

    # Filter orphan entities (not referenced by any argument)
    referenced_entity_ids = set()
    for ev in event_mentions:
        for arg in ev.get("arguments", []):
            referenced_entity_ids.add(arg["entity_id"])

    filtered_entity_mentions = [
        ent for ent in entity_mentions if ent["id"] in referenced_entity_ids
    ]

    output_rec = {
        "doc_id": doc_id,
        "sent_id": sent_id,
        "tokens": input_rec["tokens"],
        "sentence": sentence,
        "pieces": input_rec.get("pieces", []),
        "token_lens": input_rec.get("token_lens", []),
        "entity_mentions": filtered_entity_mentions,
        "event_mentions": event_mentions,
        "relation_mentions": input_rec.get("relation_mentions", []),
        "raw_response": raw_response
    }
    return output_rec


# ----------------------------------------------------------------------
# 8. Evaluation Logic (Fuzzy Bipartite Matching)
# ----------------------------------------------------------------------
def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1


def is_similar_text(t1, t2, char_threshold=0.8, word_threshold=0.66):
    """
    So sánh độ tương đồng giữa 2 chuỗi text để tính evaluation metrics.
    - char_threshold: Ngưỡng tương đồng theo ký tự (VD: 0.8 = giống nhau 80% số ký tự)
    - word_threshold: Ngưỡng tương đồng theo số lượng từ (word-level)
    """
    t1_c = str(t1).strip().lower()
    t2_c = str(t2).strip().lower()
    
    if not t1_c or not t2_c:
        return False
        
    # 1. Khớp hoàn toàn (Fast path)
    if t1_c == t2_c:
        return True
        
    # 2. Khớp theo độ tương đồng ký tự (Levenshtein distance)
    # Ví dụ: "TP.HCM" và "TP. HCM" hoặc "Hà Nôi" và "Hà Nội"
    char_sim = difflib.SequenceMatcher(None, t1_c, t2_c).ratio()
    if char_sim >= char_threshold:
        return True
        
    # 3. Khớp theo độ phủ từ (Token/Word Overlap)
    # Rất hữu ích cho entity tiếng Việt dài. 
    # Ví dụ: "Cổng thông tin điện tử Bộ Tài chính" vs "Cổng thông tin điện tử Bộ Tài chính và Kho bạc Nhà nước"
    tokens1 = set(t1_c.split())
    tokens2 = set(t2_c.split())
    
    if tokens1 and tokens2:
        intersection = tokens1.intersection(tokens2)
        
        # Tỷ lệ từ trùng lặp so với chuỗi ngắn hơn (Recall của cụm từ)
        min_len = min(len(tokens1), len(tokens2))
        max_len = max(len(tokens1), len(tokens2))
        
        overlap_ratio = len(intersection) / min_len
        global_ratio = len(intersection) / max_len
        
        # Điều kiện: Chuỗi ngắn phải nằm gần như trọn vẹn trong chuỗi dài (>= word_threshold)
        # VÀ để tránh việc 1 từ chung chung (như "ông") khớp với cả cụm dài ("ông Nguyễn Văn A"), 
        # tỷ lệ phủ trên toàn bộ chuỗi dài cũng không được quá thấp (vd: >= 0.4).
        if overlap_ratio >= word_threshold and global_ratio >= 0.4:
            return True

    return False


def evaluate_extracted_file(extracted_file, gold_file):
    print(f"\n--- Evaluation Results ---")
    print(f"Evaluating: {extracted_file}")
    print(f"Against gold: {gold_file}\n")

    gold_data = {}
    with open(gold_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rec = json.loads(line)
                gold_data[rec["sent_id"]] = rec

    pred_data = []
    with open(extracted_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                pred_data.append(json.loads(line))

    tp_emd, fp_emd, fn_emd = 0, 0, 0
    tp_ed, fp_ed, fn_ed = 0, 0, 0
    tp_eae, fp_eae, fn_eae = 0, 0, 0

    for pred_rec in pred_data:
        sent_id = pred_rec["sent_id"]
        if sent_id not in gold_data:
            continue

        gold_rec = gold_data[sent_id]

        # 1. EMD Evaluation
        gold_ents = gold_rec.get("entity_mentions", [])
        pred_ents = pred_rec.get("entity_mentions", [])

        tp_e = 0
        matched_gold_ent_indices = set()
        for p in pred_ents:
            p_text = p.get("text", "")
            p_type = p.get("entity_type", "")
            for g_idx, g in enumerate(gold_ents):
                if g_idx in matched_gold_ent_indices:
                    continue
                g_text = g.get("text", "")
                g_type = g.get("entity_type", "")
                p_text_l = p_text.strip().lower()
                g_text_l = g_text.strip().lower()
                if p_type == g_type and (
                    is_similar_text(p_text, g_text)
                    or (p_text_l and g_text_l and len(p_text_l) >= 2 and len(g_text_l) >= 2
                        and (p_text_l in g_text_l or g_text_l in p_text_l))
                ):
                    tp_e += 1
                    matched_gold_ent_indices.add(g_idx)
                    break

        tp_emd += tp_e
        fp_emd += len(pred_ents) - tp_e
        fn_emd += len(gold_ents) - tp_e

        # 2. ED Evaluation
        gold_events = gold_rec.get("event_mentions", [])
        pred_events = pred_rec.get("event_mentions", [])

        tp_v = 0
        matched_gold_ev_indices = set()
        for p in pred_events:
            p_type = p.get("event_type", "")
            p_trig = p.get("trigger", {}).get("text", "").strip().lower()
            for g_idx, g in enumerate(gold_events):
                if g_idx in matched_gold_ev_indices:
                    continue
                g_type = g.get("event_type", "")
                g_trig = g.get("trigger", {}).get("text", "").strip().lower()
                if p_type == g_type and (
                    is_similar_text(p_trig, g_trig)
                    or (p_trig and g_trig and (p_trig in g_trig or g_trig in p_trig))
                ):
                    tp_v += 1
                    matched_gold_ev_indices.add(g_idx)
                    break

        tp_ed += tp_v
        fp_ed += len(pred_events) - tp_v
        fn_ed += len(gold_events) - tp_v

        # 3. EAE Evaluation
        gold_args = []
        gold_ent_lookup = {ent["id"]: ent for ent in gold_ents}
        for ev in gold_events:
            ev_type = ev["event_type"]
            for arg in ev.get("arguments", []):
                ent_id = arg["entity_id"]
                gold_ent = gold_ent_lookup.get(ent_id)
                if gold_ent:
                    gold_args.append({
                        "event_type": ev_type,
                        "role": arg["role"],
                        "text": gold_ent.get("text", "")
                    })

        pred_args = []
        pred_ent_lookup = {ent["id"]: ent for ent in pred_ents}
        for ev in pred_events:
            ev_type = ev["event_type"]
            for arg in ev.get("arguments", []):
                ent_id = arg["entity_id"]
                pred_ent = pred_ent_lookup.get(ent_id)
                if pred_ent:
                    pred_args.append({
                        "event_type": ev_type,
                        "role": arg["role"],
                        "text": pred_ent.get("text", "")
                    })

        tp_a = 0
        matched_gold_arg_indices = set()
        for p in pred_args:
            p_ev_type = p["event_type"]
            p_role = p["role"]
            p_text = p["text"]
            for g_idx, g in enumerate(gold_args):
                if g_idx in matched_gold_arg_indices:
                    continue
                g_ev_type = g["event_type"]
                g_role = g["role"]
                g_text = g["text"]
                if p_ev_type == g_ev_type and p_role == g_role and is_similar_text(p_text, g_text):
                    tp_a += 1
                    matched_gold_arg_indices.add(g_idx)
                    break

        tp_eae += tp_a
        fp_eae += len(pred_args) - tp_a
        fn_eae += len(gold_args) - tp_a

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
# 9. Concurrent Single Record Processing Helper
# ----------------------------------------------------------------------
def process_single_record(task_args):
    idx, rec, entity_types, event_types, roles = task_args
    sentence = rec["sentence"]
    tokens = rec["tokens"]
    
    print(f"[{idx + 1}] Starting extraction...")
    token_spans = compute_token_spans(sentence, tokens)

    # === Cascade V6 Pipeline ===
    # Step 1: Extract entities (with conservative description guidance)
    entities = extract_entities_with_llm(sentence, entity_types)

    # Step 2: Extract event triggers (with vocabulary guidance)
    events_raw = extract_event_triggers_with_llm(sentence, event_types)

    # === Step 2b: Fuzzy Trigger Vocabulary Filter ===
    valid_events_raw = []
    valid_event_types_lower = {t.lower(): t for t in event_types}
    for ev in events_raw:
        trigger = ev.get("trigger", "").strip()
        ev_type = ev.get("type", "").strip()
        if not trigger or not ev_type:
            continue
        matched_type = valid_event_types_lower.get(ev_type.lower())
        if matched_type:
            ev["type"] = matched_type
            valid_events_raw.append(ev)

    # Step 3: Extract event arguments (with schema validation and conservative guidance)
    events = []
    for ev in valid_events_raw:
        trigger = ev.get("trigger", "")
        ev_type = ev.get("type", "")
        if not trigger or not ev_type:
            continue
        args = extract_event_arguments_with_llm(sentence, ev_type, trigger, entities, roles)
        events.append({
            "trigger": trigger,
            "type": ev_type,
            "arguments": args
        })

    llm_data = {
        "entities": entities,
        "events": events
    }
    raw_res = f"Cascade V6 completed. {len(entities)} entities, {len(events)} events."

    processed_rec = post_process_llm_output(
        llm_data, rec, token_spans,
        raw_response=raw_res,
        valid_entity_types=entity_types,
        valid_event_types=event_types,
        valid_roles=roles
    )
    print(f"[{idx + 1}] Finished extraction.")
    return idx, processed_rec


# ----------------------------------------------------------------------
# 10. Main Execution Flow
# ----------------------------------------------------------------------
def main():
    entity_types, event_types, roles = get_types_from_schema()

    if not entity_types or not event_types:
        print("Dynamic type extraction found no types. Aborting pipeline.")
        return

    print("Opening input file to begin extraction...")
    input_records = []
    try:
        import gzip
        open_func = gzip.open if INPUT_FILE.endswith(".gz") else open
        mode = "rt" if INPUT_FILE.endswith(".gz") else "r"
        with open_func(INPUT_FILE, mode, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    input_records.append(json.loads(line))
    except FileNotFoundError:
        print(f"Error: file {INPUT_FILE} not found.")
        return

    total_records = len(input_records)
    if MAX_SAMPLES is not None:
        if MAX_SAMPLES < total_records:
            input_records = input_records[:MAX_SAMPLES]
        print(f"Running V6 LLM extraction on the first {MAX_SAMPLES} out of {total_records} records.")
    else:
        print(f"Running V6 LLM extraction on all {total_records} records.")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    print(f"Writing directly to {OUTPUT_FILE} line by line using {NUM_THREADS} threads concurrently...")

    # Pack task arguments
    tasks = []
    for idx, rec in enumerate(input_records):
        tasks.append((idx, rec, entity_types, event_types, roles))

    # Run thread pool and write outputs in the EXACT original sequential order
    with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
        futures = [executor.submit(process_single_record, task) for task in tasks]
        
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
            for future in futures:
                task_idx, processed_rec = future.result()
                out.write(json.dumps(processed_rec, ensure_ascii=False) + "\n")
                out.flush()
                print(f"[{task_idx + 1}/{len(input_records)}] Written to {OUTPUT_FILE}")

    print(f"\nCompleted! Output written to {OUTPUT_FILE}")
    evaluate_extracted_file(OUTPUT_FILE, INPUT_FILE)


if __name__ == "__main__":
    main()
