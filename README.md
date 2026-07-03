# Vietnamese Silver Event Extraction & Natural Reasoning Pipeline

An end-to-end framework for Vietnamese Event Extraction (EE) utilizing distant supervision, LLM-generated step-by-step natural reasoning, structural validation, and multi-device LoRA fine-tuning.

---

## 🌟 Table of Contents
1. [Overview](#-overview)
2. [Dataset Description (BKEE)](#-dataset-description-bkee)
3. [Distant Supervision & Reasoning Pipeline](#-distant-supervision--reasoning-pipeline)
4. [Dynamic Multi-Device Training Support](#-dynamic-multi-device-training-support)
5. [Getting Started](#-getting-started)
6. [Project Structure](#-project-structure)
7. [Citation](#-citation)

---

## 🚀 Overview
This repository hosts an advanced Vietnamese Event Extraction pipeline. It leverages the **BKEE** dataset (a pioneering event extraction resource for Vietnamese) and augments it by:
1. Generating high-quality, step-by-step **Natural Reasoning** (Chain-of-Thought) data using Large Language Models.
2. Building a resilient, parallelized generation script featuring **real-time database appending, Pydantic verification, and checkpoint resumption**.
3. Training reasoning-aware extractors using **LoRA / QLoRA** under a dynamic device-aware backend (supporting Apple Silicon MLX, CUDA, MPS, and CPU).

---

## 📊 Dataset Description (BKEE)
**BKEE** is a pioneering annotated dataset for Vietnamese Event Extraction introduced at **LREC-COLING 2024**.

### Key Statistics
* **33+ distinct event types** covering diverse domains.
* **28 different event argument roles** capturing semantic contexts.
* **1,066 manually labeled documents** annotated with entity mentions, event triggers, and arguments.

### Format
The data resides in the `dataset/` directory as JSONL files. Each line represents a tokenized sentence with its gold entities and events:

```json
{
    "doc_id": "test-00000",
    "sent_id": "test-00000",
    "tokens": ["Chiều", "1/12", ",", "anh", "Đặng Duy Thông", "(", "36", "tuổi", ")", "chạy", "xe máy", "."],
    "sentence": "Chiều 1/12 , anh Đặng Duy Thông ( 36 tuổi ) chạy xe máy .",
    "entity_mentions": [
        {"id": "test-T1", "text": "Đặng Duy Thông", "entity_type": "Person", "start": 4, "end": 6}
    ],
    "event_mentions": [
        {
            "id": "test-EV1",
            "event_type": "Movement:Transport",
            "trigger": {"text": "chạy", "start": 9, "end": 10},
            "arguments": [
                {"entity_id": "test-T1", "text": "Đặng Duy Thông", "role": "Agent"}
            ]
        }
    ]
}
```

---

## 🧠 Distant Supervision & Reasoning Pipeline

The pipeline translates abstract distant supervision labels into natural language reasoning traces (Chain-of-Thought) that guide subsequent extraction tasks.

### 1. Data Builders & Natural Reasoning
We split reasoning generation into four distinct builders located under `apps/data_builder/`:
* **EntityBuilder**: Explains how candidate spans map to core entity types (Person, Organization, Job, etc.).
* **EventBuilder**: Highlights key trigger words evoking specific events.
* **ArgumentBuilder**: Links identified entities to their semantic roles under a trigger.
* **FullBuilder**: Combines the three preceding stages into a single holistic extraction thought process.

### 2. Guardrails & Validation
* **Pydantic Schemas**: Every LLM prediction is locally validated against a Pydantic schema structure inside each builder.
* **Auto-Retries**: Queries failing validation or encountering API limits are automatically retried up to 3 times via an exponential back-off wrapper.
* **Gold-Standard Alignments**:
  * For single-phase extractors, predictions are strictly matched against non-empty gold labels. If gold labels are empty, predictions are permitted to capture missed elements.
  * For the full extractor pipeline, gold labels are treated as absolute truths. Directives guide the LLM to justify why zero entities/events were found when target labels are empty.

### 3. Checkpoint Resumption & Skip Logic
Running generation tasks over thousands of items can be interrupted. The pipeline protects against data loss:
* **Real-time Appends**: Completed samples are written immediately to target files in append mode.
* **Robust Loaders**: If interrupted (e.g., via `Ctrl+C`), target loaders ignore any trailing malformed/partially written lines.
* **Auto-Skip**: On restarts, the builder counts completed samples in target files and automatically slices candidate queues to skip already processed items.

---

## 💻 Dynamic Multi-Device Training Support
The fine-tuning script automatically detects hardware capabilities and routes execution to the optimal backend:

| Device Type | Accelerator Backend | Quantization / Precision | Trainer |
| :--- | :--- | :--- | :--- |
| **MLX (macOS)** | Apple Silicon Metal | Native MLX float16 | `MLXTrainer` (Unsloth MLX) |
| **CUDA (Nvidia)** | PyTorch CUDA | 4-bit QLoRA / fp16 or bf16 | `SFTTrainer` (trl) + Unsloth |
| **MPS (macOS Torch)** | PyTorch Metal | Float16 | `SFTTrainer` (trl) + PEFT |
| **CPU** | PyTorch CPU | Float32 | `SFTTrainer` (trl) + PEFT |

---

## 🛠️ Getting Started

### 1. Installation
Install the project dependencies in a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Setup
Configure your API keys in a `.env` file in the root directory:
```env
GEMINI_API_KEY="your-gemini-api-key"
```

### 3. Running Data Generation
Generate reasoning datasets for a specific phase (`entity`, `event`, `argument`, or `full`):
```bash
python main.py --build_data full --n_jobs 4
```
*Note: If a process is stopped, running the same command again will resume from the last completed sentence.*

### 4. Model Training
Run fine-tuning on the generated datasets:
```bash
python main.py --train --phase full --max_steps 600
```

---

## 📁 Project Structure
```
.
├── apps/
│   ├── data_builder/       # Entity, Event, Argument, and Full reasoning builders
│   ├── evaluators/         # Metrics and scoring evaluators for predictions
│   ├── extractors/         # Extraction logic using fine-tuned models
│   ├── trainers/           # Model converters, trainers, and checkpoints
│   ├── constants.py        # Prompts, entity mappings, and schemas
│   └── models.py           # Core Pydantic and dataclass model layers
├── dataset/                # Raw BKEE JSONL data & generated silver reasoning datasets
├── main.py                 # Main orchestration runner (data building, training, evaluation)
├── requirements.txt        # PIP dependencies
└── DESIGN.md               # Architecture design document
```

---

## 📝 Citation
If you use the BKEE dataset or this pipeline in your research, please cite:

```bibtex
@inproceedings{nguyen-etal-2024-bkee,
    title = "{BKEE}: Pioneering Event Extraction in the {V}ietnamese Language",
    author = "Nguyen, Thi-Nhung  and
      Tran, Bang Tien  and
      Luu, Trong-Nghia  and
      Nguyen, Thien Huu  and
      Nguyen, Kiem-Hieu",
    booktitle = "Proceedings of the 2024 Joint International Conference on Computational Linguistics, Language Resources and Evaluation (LREC-COLING 2024)",
    month = may,
    year = "2024",
    address = "Torino, Italia",
    publisher = "ELRA and ICCL",
    url = "https://aclanthology.org/2024.lrec-main.217",
    pages = "2421--2427"
}
```
