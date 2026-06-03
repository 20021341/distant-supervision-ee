import json
import os
import glob
from collections import defaultdict, Counter
from openai import OpenAI

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
DEFAULT_EXTRACTION_FILE = "final_data/processed_enriched_med/train_llm_extracted_med_v1_20260602_141850.json"
DOCUMENTS_FILE = "final_data/processed_enriched_med/documents.json"
BASE_URL = "https://openrouter.ai/api/v1"
API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "google/gemma-4-26b-a4b-it"

# Initialize OpenAI client using OpenRouter
try:
    if not API_KEY:
        print("Warning: OPENROUTER_API_KEY environment variable is not set.")
    client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    client = None

def get_latest_extraction_file():
    pattern = "final_data/processed_enriched_med/train_llm_extracted_med_*.json"
    files = glob.glob(pattern)
    if files:
        files.sort(key=os.path.getmtime, reverse=True)
        return files[0]
    return DEFAULT_EXTRACTION_FILE

def load_doc_urls():
    doc_url_map = {}
    if os.path.exists(DOCUMENTS_FILE):
        with open(DOCUMENTS_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                    doc_id = rec.get("doc_id")
                    url = rec.get("url")
                    if doc_id and url and doc_id not in doc_url_map:
                        doc_url_map[doc_id] = url
                except json.JSONDecodeError:
                    pass
    return doc_url_map

def get_rich_statistics(extraction_file, doc_url_map, top_n_events=8, top_n_pairs=10, sample_limit=5):
    """
    Thống kê phi thiên vị (unbiased) kết hợp cả sự kiện lẫn thực thể đồng xuất hiện.
    """
    stop_entities = {
        "bác sĩ", "người bệnh", "bệnh nhân", "trẻ", "bệnh nhi", 
        "y bác sĩ", "bé", "người", "cháu", "các bác sĩ", 
        "bệnh", "bệnh viện", "khoa", "điều trị", "khám"
    }

    event_counts = Counter()
    event_details = defaultdict(lambda: {
        "triggers": Counter(),
        "arguments": defaultdict(Counter),
        "samples": []
    })
    
    entity_counts = Counter()
    sentence_pairs = Counter()
    pair_samples = defaultdict(list)

    with open(extraction_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line.strip())
            
            doc_id = rec.get("doc_id", "Unknown")
            url = doc_url_map.get(doc_id, "Không có link")
            sentence = rec.get("sentence", "").strip()
            
            # --- A. Thống kê Sự kiện ---
            for ev in rec.get("event_mentions", []):
                ev_type = ev.get("event_type")
                trigger = ev.get("trigger", {}).get("text", "").strip()
                event_counts[ev_type] += 1
                
                if trigger:
                    event_details[ev_type]["triggers"][trigger] += 1
                for arg in ev.get("arguments", []):
                    role = arg.get("role")
                    text = arg.get("text", "").strip()
                    if role and text:
                        event_details[ev_type]["arguments"][role][text] += 1
                        
                if len(event_details[ev_type]["samples"]) < sample_limit:
                    if sentence not in [s["sentence"] for s in event_details[ev_type]["samples"]]:
                        event_details[ev_type]["samples"].append({
                            "doc_id": doc_id,
                            "url": url,
                            "sentence": sentence,
                            "trigger": trigger,
                            "args": [{ "role": arg.get("role"), "text": arg.get("text") } for arg in ev.get("arguments", [])]
                        })

            # --- B. Thống kê Thực thể & Đồng xuất hiện ---
            ents_in_sent = list(set([ent.get("text").strip() for ent in rec.get("entity_mentions", [])]))
            for text in ents_in_sent:
                entity_counts[text] += 1
                
            for i in range(len(ents_in_sent)):
                for j in range(i + 1, len(ents_in_sent)):
                    e1, e2 = ents_in_sent[i].lower(), ents_in_sent[j].lower()
                    if e1 not in stop_entities and e2 not in stop_entities and e1 != e2:
                        pair = tuple(sorted([e1, e2]))
                        sentence_pairs[pair] += 1
                        
                        if len(pair_samples[pair]) < sample_limit:
                            if sentence not in [s["sentence"] for s in pair_samples[pair]]:
                                pair_samples[pair].append({
                                    "doc_id": doc_id,
                                    "url": url,
                                    "sentence": sentence
                                })

    structured_events = []
    for ev_type, count in event_counts.most_common(top_n_events):
        details = event_details[ev_type]
        top_triggers = [t for t, _ in details["triggers"].most_common(5)]
        top_args = {}
        for role, texts_counter in details["arguments"].items():
            top_args[role] = [t for t, _ in texts_counter.most_common(3)]
            
        structured_events.append({
            "event_type": ev_type,
            "total_occurrences": count,
            "common_triggers": top_triggers,
            "common_arguments": top_args,
            "sample_sentences": details["samples"]
        })
        
    structured_stories = []
    for pair, count in sentence_pairs.most_common(top_n_pairs):
        structured_stories.append({
            "entity_1": pair[0],
            "entity_2": pair[1],
            "co_occurrence_count": count,
            "sample_news_sentences": pair_samples[pair]
        })

    return {
        "event_statistics": structured_events,
        "entity_co_occurrences": structured_stories
    }

def synthesize_hot_stories_with_llm(stats_payload):
    if not client:
        print("❌ OpenAI client chưa được khởi tạo. Không thể gọi LLM tổng hợp.")
        return None

    system_prompt = """Bạn là một chuyên gia cao cấp về Giám sát truyền thông và Social Listening trong lĩnh vực Y tế tại Việt Nam.
Nhiệm vụ của bạn là phân tích dữ liệu thống kê sự kiện và thực thể y tế thô ngày 01/06/2026.

Dữ liệu đầu vào bao gồm hai phần:
1. **event_statistics**: Các sự kiện lâm sàng xuất hiện nhiều nhất, triggers/arguments đi kèm và câu gốc mẫu.
2. **entity_co_occurrences**: Các cặp thực thể y tế chuyên môn đồng xuất hiện nhiều nhất trong cùng một câu, kèm theo câu gốc thực tế.

CHỈ THỊ QUAN TRỌNG:
- Bạn BẮT BUỘC phải trích xuất và tổng hợp thành CHÍNH XÁC 5 SỰ KIỆN/CHỦ ĐỀ nóng nhất, không hơn không kém.
- Bạn BẮT BUỘC phải tuân thủ tuyệt đối định dạng Markdown mẫu dưới đây, KHÔNG ĐƯỢC TỰ Ý THAY ĐỔI CẤU TRÚC.
- Phải có phần "DỰ BÁO XU HƯỚNG" ở cuối dựa trên những thông tin có khả năng tiếp tục thu hút dư luận (ví dụ: diễn biến dịch bệnh, chính sách mới, sai phạm y tế cần điều tra thêm...).

================ TEMPLATE BẮT BUỘC ================
# BẢN TIN GIÁM SÁT TRUYỀN THÔNG Y TẾ - NGÀY 01/06/2026

## I. TỔNG HỢP 5 CHỦ ĐỀ TRUYỀN THÔNG NỔI BẬT NHẤT

### 1. [Tên Chủ đề/Sự kiện 1 - Viết ngắn gọn, thu hút]
- **Mức độ nóng:** [Tổng số lần nhắc đến từ dữ liệu]
- **Tóm tắt nội dung:** [Viết 2-3 câu tóm tắt khách quan sự kiện dựa trên các sample_sentences]
- **Thực thể tham gia chính:** [Liệt kê các bệnh viện, cá nhân, loại bệnh, thuốc... cốt lõi]
- **Bài báo nổi bật:** [doc-id](url)
  > "[Trích dẫn trực tiếp 1-2 câu tiêu biểu từ bài báo này]"

### 2. [Tên Chủ đề/Sự kiện 2]
- **Mức độ nóng:** [...]
- **Tóm tắt nội dung:** [...]
- **Thực thể tham gia chính:** [...]
- **Bài báo nổi bật:** [doc-id](url)
  > "[Trích dẫn]"

### 3. [Tên Chủ đề/Sự kiện 3]
... (Làm tương tự cho đến mục số 5)

## II. DỰ BÁO XU HƯỚNG TRUYỀN THÔNG TỚI
- **Xu hướng 1:** [Phân tích ngắn gọn chủ đề nào có thể tiếp tục nóng lên hoặc thu hút sự quan tâm trong 24-48h tới dựa trên dữ liệu hiện tại]
- **Xu hướng 2:** [Phân tích thêm 1 khía cạnh khác có nguy cơ khủng hoảng truyền thông hoặc cần theo dõi sát sao]
==================================================
"""

    user_prompt = f"Dưới đây là dữ liệu thống kê sự kiện y tế thô ngày 1/6:\n{json.dumps(stats_payload, ensure_ascii=False, indent=2)}\n\nHãy xuất báo cáo TUYỆT ĐỐI tuân theo template đã cung cấp."
    
    print("🤖 Đang gửi dữ liệu thống kê lên LLM để phân tích và tổng hợp tự động...")
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2 # Giảm temperature xuống 0.2 để mô hình bám sát template thay vì sáng tạo
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ Lỗi khi gọi LLM: {e}")
        return None

def main():
    extraction_file = get_latest_extraction_file()
    print(f"🔄 Đang đọc dữ liệu từ tệp trích xuất: {extraction_file}")
    
    if not os.path.exists(extraction_file):
        print(f"❌ Không tìm thấy tệp {extraction_file}. Vui lòng chạy trích xuất LLM trước.")
        return

    print("🔗 Đang ánh xạ URL bài báo từ file documents.json...")
    doc_url_map = load_doc_urls()

    # Truyền top_n_events=8, top_n_pairs=10 để LLM có đủ dữ liệu chọn ra chính xác 5 chủ đề
    print("📊 Đang phân tích và lập bảng thống kê sự kiện & thực thể từ tệp trích xuất...")
    stats_payload = get_rich_statistics(extraction_file, doc_url_map, top_n_events=8, top_n_pairs=10, sample_limit=8)
    
    # 2. Sử dụng LLM tổng hợp thông minh
    summary_report = synthesize_hot_stories_with_llm(stats_payload)
    
    if summary_report:
        print("\n" + "="*80)
        print(summary_report)
        print("="*80)
    else:
        print("\n❌ Gặp lỗi khi tổng hợp bằng LLM. Dưới đây là thống kê thô:")
        print(json.dumps(stats_payload, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()