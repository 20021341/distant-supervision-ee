import json
import torch
from datasets import Dataset
from unsloth import FastLanguageModel

# ----------------------------------------------------------------------
# 1. Configuration Constants
# ----------------------------------------------------------------------
import os
INPUT_FILE = "final_data/processed_enriched_3/train.json.gz"
if not os.path.exists(INPUT_FILE):
    INPUT_FILE = "final_data/processed_enriched_3/train.json"
MODEL_NAME = "Qwen/Qwen3.5-0.8B"  # Base model choice (e.g. Qwen-2.5, Llama-3, etc.)
MAX_SEQ_LENGTH = 2048
OUTPUT_DIR = "unsloth_full_finetuned_outputs"
FINAL_MODEL_DIR = "unsloth_full_finetuned_model"
MAX_STEPS = 600             # Adjust this to train longer (e.g. 1000, 2000, etc.)

# ----------------------------------------------------------------------
# 2. Data Preparation & Minimalist Serialization
# ----------------------------------------------------------------------
print("Reading and parsing train.json dataset...")
sentences = []
target_jsons = []

import gzip
open_func = gzip.open if INPUT_FILE.endswith(".gz") else open
mode = "rt" if INPUT_FILE.endswith(".gz") else "r"
with open_func(INPUT_FILE, mode, encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
            sentence = rec.get("sentence", "")
            if not sentence:
                continue

            # A. Process Entities
            gold_ents = rec.get("entity_mentions", [])
            entity_lookup = {}
            entities_mapped = []
            for ent in gold_ents:
                ent_id = ent.get("id")
                ent_text = ent.get("text", "")
                ent_type = ent.get("entity_type", "")
                if ent_id:
                    entity_lookup[ent_id] = ent_text
                entities_mapped.append({
                    "type": ent_type,
                    "text": ent_text
                })

            # B. Process Events
            gold_events = rec.get("event_mentions", [])
            events_mapped = []
            for ev in gold_events:
                ev_type = ev.get("event_type", "")
                trigger_text = ev.get("trigger", {}).get("text", "")
                
                args_mapped = []
                for arg in ev.get("arguments", []):
                    ent_id = arg.get("entity_id")
                    role = arg.get("role", "")
                    ent_text = entity_lookup.get(ent_id, "")
                    args_mapped.append({
                        "type": role,
                        "text": ent_text
                    })

                events_mapped.append({
                    "type": ev_type,
                    "trigger": trigger_text,
                    "arguments": args_mapped
                })

            # C. Serialize to target JSON string (using compact separators to minimize token size)
            target_data = {
                "entities": entities_mapped,
                "events": events_mapped
            }
            target_json_str = json.dumps(target_data, separators=(',', ':'), ensure_ascii=False)

            sentences.append(sentence)
            target_jsons.append(target_json_str)

        except Exception as e:
            print(f"Error parsing line: {e}")

print(f"Successfully processed {len(sentences)} training samples.")

# Create HuggingFace Dataset
dataset = Dataset.from_dict({
    "sentence": sentences,
    "target_json": target_jsons
})

# ----------------------------------------------------------------------
# 3. Chat Prompt Formatting (Minimalist System + User)
# ----------------------------------------------------------------------
def format_prompts(examples):
    texts = []
    for sentence, target_json in zip(examples["sentence"], examples["target_json"]):
        # Minimalist chat prompt structure (using ChatML format)
        text = (
            "<|im_start|>system\n"
            "Bạn là một trợ lý trích xuất thực thể và sự kiện tiếng Việt chuyên nghiệp.\n"
            "<|im_end|>\n"
            "<|im_start|>user\n"
            f"Trích xuất thực thể và sự kiện dưới dạng JSON từ câu sau:\n"
            f"\"{sentence}\"\n"
            "<|im_end|>\n"
            "<|im_start|>assistant\n"
            f"{target_json}\n"
            "<|im_end|>"
        )
        texts.append(text)
    return {"text": texts}

print("Formatting prompt template...")
formatted_dataset = dataset.map(format_prompts, batched=True)

# ----------------------------------------------------------------------
# 4. Load Unsloth FastLanguageModel for Full Fine-Tuning (FFT)
# ----------------------------------------------------------------------
print(f"Initializing FastLanguageModel for Full Fine-Tuning: {MODEL_NAME}...")

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = MODEL_NAME,
    max_seq_length = MAX_SEQ_LENGTH,
    dtype = None,               # Auto detect float16 (T4, V100) or bfloat16 (Ampere+)
    load_in_4bit = False,       # MUST be False for full parameter fine-tuning
    full_finetuning = True      # MUST be True to train all weights in Unsloth
)

# ----------------------------------------------------------------------
# 5. Trainer Setup & Training Arguments (Cross-Platform)
# ----------------------------------------------------------------------
import unsloth
is_mlx = getattr(unsloth, "_IS_MLX", False)

if is_mlx:
    # macOS Apple Silicon / MLX training logic
    from unsloth import MLXTrainer, MLXTrainingConfig
    print("Detected macOS/MLX environment. Importing MLXTrainer and MLXTrainingConfig...")
    
    trainer = MLXTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = formatted_dataset,
        args = MLXTrainingConfig(
            dataset_text_field = "text",
            max_seq_length = MAX_SEQ_LENGTH,
            packing = False,
            per_device_train_batch_size = 4,
            gradient_accumulation_steps = 4,
            warmup_steps = 100,
            max_steps = MAX_STEPS,
            learning_rate = 2e-5,
            optim = "adamw",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = OUTPUT_DIR,
            dataset_num_proc = 4,
            logging_steps = 10
        )
    )
else:
    # CUDA/Torch training logic with Early Stopping
    from trl import SFTTrainer, SFTConfig
    from transformers import EarlyStoppingCallback
    print("Detected CUDA/Torch environment. Preparing SFTTrainer with Early Stopping...")
    
    # Auto-detect hardware optimization
    has_bf16 = torch.cuda.is_bf16_supported()
    
    # Split dataset for validation (90% train, 10% eval)
    split_dataset = formatted_dataset.train_test_split(test_size=0.1, seed=3407)
    train_dataset = split_dataset["train"]
    eval_dataset = split_dataset["test"]
    
    trainer = SFTTrainer(
        model = model,
        processing_class = tokenizer,
        train_dataset = train_dataset,
        eval_dataset = eval_dataset,
        callbacks = [EarlyStoppingCallback(early_stopping_patience=3)],
        args = SFTConfig(
            dataset_text_field = "text",
            max_length = MAX_SEQ_LENGTH,
            dataset_num_proc = 4,
            packing = False,
            per_device_train_batch_size = 4,
            gradient_accumulation_steps = 4,
            warmup_steps = 100,
            max_steps = MAX_STEPS,
            learning_rate = 2e-5,
            fp16 = not has_bf16,
            bf16 = has_bf16,
            logging_steps = 10,
            eval_strategy = "steps",
            eval_steps = 50,
            save_strategy = "steps",
            save_steps = 50,
            save_total_limit = 2,
            load_best_model_at_end = True,
            metric_for_best_model = "loss",
            greater_is_better = False,
            optim = "adamw_8bit" if has_bf16 else "adamw_torch",
            weight_decay = 0.01,
            lr_scheduler_type = "linear",
            seed = 3407,
            output_dir = OUTPUT_DIR,
            report_to = "none"
        )
    )

# ----------------------------------------------------------------------
# 6. Execute Training
# ----------------------------------------------------------------------
print("Starting Unsloth Full Parameter Fine-Tuning...")
trainer_stats = trainer.train()

# ----------------------------------------------------------------------
# 7. Save Model & Tokenizer
# ----------------------------------------------------------------------
print(f"Saving final full parameters model to: {FINAL_MODEL_DIR}...")
if is_mlx:
    # macOS/MLX saving logic for Full Parameter Fine-Tuning
    model.save_pretrained_merged(FINAL_MODEL_DIR, tokenizer=tokenizer, save_method="merged_16bit")
else:
    # CUDA/Torch saving logic
    model.save_pretrained(FINAL_MODEL_DIR)
    tokenizer.save_pretrained(FINAL_MODEL_DIR)

print("\nFull parameter training complete and model saved successfully! 🎉")

# ----------------------------------------------------------------------
# 8. Post-Training Evaluation
# ----------------------------------------------------------------------
print("\n=== Running Post-Training Evaluation on first 50 samples ===")

import difflib

def is_similar_text(t1, t2, char_threshold=0.8, word_threshold=0.66):
    t1_c = str(t1).strip().lower()
    t2_c = str(t2).strip().lower()
    if not t1_c or not t2_c:
        return False
    if t1_c == t2_c:
        return True
    char_sim = difflib.SequenceMatcher(None, t1_c, t2_c).ratio()
    if char_sim >= char_threshold:
        return True
    tokens1 = set(t1_c.split())
    tokens2 = set(t2_c.split())
    if tokens1 and tokens2:
        intersection = tokens1.intersection(tokens2)
        min_len = min(len(tokens1), len(tokens2))
        max_len = max(len(tokens1), len(tokens2))
        if len(intersection) / min_len >= word_threshold and len(intersection) / max_len >= 0.4:
            return True
    return False

def generate_response(model, tokenizer, prompt, max_tokens=1024):
    if is_mlx:
        from mlx_vlm import generate
        out = generate(model, tokenizer, prompt, image=None, verbose=False, max_tokens=max_tokens)
        return out.text
    else:
        FastLanguageModel.for_inference(model)
        inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
        outputs = model.generate(**inputs, max_new_tokens=max_tokens, use_cache=True)
        input_len = inputs.input_ids.shape[1]
        new_outputs = outputs[0][input_len:]
        return tokenizer.decode(new_outputs, skip_special_tokens=True).strip()

def parse_json_robust(content):
    content = content.strip()
    if "```json" in content:
        content = content.split("```json")[1].split("```")[0]
    elif "```" in content:
        content = content.split("```")[1]
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1:
        content = content[start:end+1]
    try:
        return json.loads(content)
    except Exception:
        return {}

def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    return precision, recall, f1

# Read first 50 samples from INPUT_FILE
eval_records = []
open_func = gzip.open if INPUT_FILE.endswith(".gz") else open
mode = "rt" if INPUT_FILE.endswith(".gz") else "r"
with open_func(INPUT_FILE, mode, encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 50:
            break
        if line.strip():
            eval_records.append(json.loads(line))

tp_emd, fp_emd, fn_emd = 0, 0, 0
tp_ed, fp_ed, fn_ed = 0, 0, 0
tp_eae, fp_eae, fn_eae = 0, 0, 0

for idx, rec in enumerate(eval_records):
    sentence = rec.get("sentence", "")
    if not sentence:
        continue
    
    # Format Prompt
    prompt = (
        "<|im_start|>system\n"
        "Bạn là một trợ lý trích xuất thực thể và sự kiện tiếng Việt chuyên nghiệp.\n"
        "<|im_end|>\n"
        "<|im_start|>user\n"
        f"Trích xuất thực thể và sự kiện dưới dạng JSON từ câu sau:\n"
        f"\"{sentence}\"\n"
        "<|im_end|>\n"
        "<|im_start|>assistant\n"
    )
    
    # Generate
    pred_str = generate_response(model, tokenizer, prompt, max_tokens=1024)
    pred_data = parse_json_robust(pred_str)
    
    pred_ents = pred_data.get("entities", [])
    pred_events = pred_data.get("events", [])
    
    # Gold labels
    gold_ents = rec.get("entity_mentions", [])
    gold_events = rec.get("event_mentions", [])
    
    # EMD Match
    tp_e, matched_g_e = 0, set()
    for p in pred_ents:
        p_type = p.get("type", "")
        p_text = p.get("text", "")
        for g_idx, g in enumerate(gold_ents):
            if g_idx in matched_g_e:
                continue
            g_type = g.get("entity_type", "")
            g_text = g.get("text", "")
            if p_type == g_type and is_similar_text(p_text, g_text):
                tp_e += 1
                matched_g_e.add(g_idx)
                break
    tp_emd += tp_e
    fp_emd += len(pred_ents) - tp_e
    fn_emd += len(gold_ents) - tp_e

    # ED Match
    tp_v, matched_g_v = 0, set()
    for p in pred_events:
        p_type = p.get("type", "")
        p_trig = p.get("trigger", "")
        for g_idx, g in enumerate(gold_events):
            if g_idx in matched_g_v:
                continue
            g_type = g.get("event_type", "")
            g_trig = g.get("trigger", {}).get("text", "")
            if p_type == g_type and is_similar_text(p_trig, g_trig):
                tp_v += 1
                matched_g_v.add(g_idx)
                break
    tp_ed += tp_v
    fp_ed += len(pred_events) - tp_v
    fn_ed += len(gold_events) - tp_v

    # EAE Match
    gold_ent_lookup = {e["id"]: e["text"] for e in gold_ents}
    gold_args = []
    for ev in gold_events:
        ev_type = ev["event_type"]
        for arg in ev.get("arguments", []):
            gold_args.append({
                "event_type": ev_type,
                "role": arg["role"],
                "text": gold_ent_lookup.get(arg["entity_id"], "")
            })
            
    pred_args = []
    for ev in pred_events:
        ev_type = ev.get("type", "")
        for arg in ev.get("arguments", []):
            pred_args.append({
                "event_type": ev_type,
                "role": arg.get("type", ""),
                "text": arg.get("text", "")
            })
            
    tp_a, matched_g_a = 0, set()
    for p in pred_args:
        for g_idx, g in enumerate(gold_args):
            if g_idx in matched_g_a:
                continue
            if p["event_type"] == g["event_type"] and p["role"] == g["role"] and is_similar_text(p["text"], g["text"]):
                tp_a += 1
                matched_g_a.add(g_idx)
                break
    tp_eae += tp_a
    fp_eae += len(pred_args) - tp_a
    fn_eae += len(gold_args) - tp_a

prec_emd, rec_emd, f1_emd = calculate_metrics(tp_emd, fp_emd, fn_emd)
prec_ed, rec_ed, f1_ed = calculate_metrics(tp_ed, fp_ed, fn_ed)
prec_eae, rec_eae, f1_eae = calculate_metrics(tp_eae, fp_eae, fn_eae)

print("\n" + "="*50)
print("FINAL EVALUATION RESULTS (POST-TRAINING):")
print("="*50)
print(f"1. EMD — Prec: {prec_emd:.4f} | Rec: {rec_emd:.4f} | F1: {f1_emd:.4f}")
print(f"2. ED  — Prec: {prec_ed:.4f} | Rec: {rec_ed:.4f} | F1: {f1_ed:.4f}")
print(f"3. EAE — Prec: {prec_eae:.4f} | Rec: {rec_eae:.4f} | F1: {f1_eae:.4f}")
print("="*50 + "\n")
