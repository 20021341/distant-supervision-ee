import os
import csv
import json
import re
import time
import logging
from datetime import datetime, timezone
from typing import List, Union, Dict, Any, Optional

from pydantic import BaseModel

from apps.helpers.dataset_loader import load_base_dataset
from apps.helpers.llm_caller import make_llm_caller
from apps.constants import (
    FINETUNED_ENTITIES_SYSTEM_PROMPT,
    FINETUNED_EVENTS_SYSTEM_PROMPT,
    FINETUNED_ARGUMENTS_SYSTEM_PROMPT,
    FINETUNED_FULL_SYSTEM_PROMPT,
)
from apps.extractors.entity_extractor import EntityExtractor
from apps.extractors.event_extractor import EventExtractor
from apps.extractors.argument_assigner import ArgumentAssigner
from apps.extractors.full_extractor import FullExtractor
from apps.extractors.pipeline_extractor import PipelineExtractor
from apps.evaluators.entity_evaluator import EntityEvaluator
from apps.evaluators.event_evaluator import EventEvaluator
from apps.evaluators.argument_evaluator import ArgumentEvaluator
from apps.evaluators.full_evaluator import FullEvaluator
from apps.evaluators.pipeline_evaluator import PipelineEvaluator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CSV_FIELDNAMES = [
    "timestamp",
    "model",
    "model_source",
    "phase",
    "sample_rate",
    "n_samples",
    "options",
    "duration_seconds",
    "precision",
    "recall",
    "f1",
    "output_file",
]


def _to_jsonable(obj: Any) -> Any:
    if obj is None:
        return None
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(o) for o in obj]
    return obj


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "_", value.strip())
    return slug.strip("_") or "model"


def _dump_predictions(evaluator: Any, output_path: str) -> None:
    sentences = getattr(evaluator, "last_sentences", [])
    predictions = getattr(evaluator, "last_predictions", [])
    gold = getattr(evaluator, "last_gold", [])

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for i in range(len(predictions)):
            row = {
                "sentence": sentences[i] if i < len(sentences) else None,
                "prediction": _to_jsonable(predictions[i]),
                "gold": _to_jsonable(gold[i]) if i < len(gold) else None,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _append_csv_row(csv_path: str, row: Dict[str, Any]) -> None:
    parent_dir = os.path.dirname(os.path.abspath(csv_path))
    os.makedirs(parent_dir, exist_ok=True)
    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def run_evaluation(
    eval_model: str,
    sample: Union[int, float] = 1.0,
    n_jobs: int = 5,
    include_hints: bool = True,
    few_shot: bool = False,
    csv_path: str = "eval_results.csv",
    output_dir: str = "eval_outputs",
    max_seq_length: int = 2048,
    phases: Optional[List[str]] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Runs entity, event, argument, pipeline (entity -> event -> argument) and
    full (single-call) evaluation on the test split for the given model, then
    appends one CSV row per phase to `csv_path` and dumps raw predictions for
    each phase to a JSONL file under `output_dir`.

    `eval_model` is either an OpenRouter model identifier, or an absolute/relative
    path to a finetuned checkpoint. Pass `base_url` to instead hit any OpenAI-compatible
    HTTP endpoint (e.g. a local vLLM server) with `eval_model` as the served model name --
    this uses the same fixed finetuned system prompts as a local checkpoint, since the
    served model is assumed to be a finetuned checkpoint too, and supports full
    concurrency (`n_jobs`) since the server handles request batching itself.

    `phases`: subset of {"entity", "event", "argument", "pipeline", "full"} to run.
    Defaults to all five when omitted/empty.
    """
    is_served = base_url is not None
    is_local = (not is_served) and os.path.exists(eval_model)
    model_source = "vllm" if is_served else ("local_checkpoint" if is_local else "openrouter")
    logger.info(f"=== Starting evaluation for model: {eval_model} ({model_source}) ===")

    dataset = load_base_dataset("test")
    n_records = len(dataset.items)
    n_samples = int(n_records * sample) if isinstance(sample, float) else min(sample, n_records)

    if is_served or is_local:
        options_label = "n/a (finetuned checkpoint uses fixed system prompts)"
    else:
        enabled = [name for name, flag in [("include_hints", include_hints), ("few_shot", few_shot)] if flag]
        options_label = ",".join(enabled) if enabled else "none"

    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    model_slug = _slugify(os.path.basename(eval_model.rstrip("/\\")) or eval_model)

    finetuned_model = None
    if is_served:
        caller = make_llm_caller(eval_model, base_url=base_url, api_key=api_key)

        entity_extractor = EntityExtractor(llm_caller_func=caller, system_prompt=FINETUNED_ENTITIES_SYSTEM_PROMPT)
        event_extractor = EventExtractor(llm_caller_func=caller, system_prompt=FINETUNED_EVENTS_SYSTEM_PROMPT)
        argument_assigner = ArgumentAssigner(llm_caller_func=caller, system_prompt=FINETUNED_ARGUMENTS_SYSTEM_PROMPT)
        full_extractor = FullExtractor(llm_caller_func=caller, system_prompt=FINETUNED_FULL_SYSTEM_PROMPT)
    elif is_local:
        if n_jobs != 1:
            logger.warning("Local checkpoint inference is not thread-safe; forcing n_jobs=1.")
        n_jobs = 1

        from apps.trainers.inference_models import FinetunedModel
        finetuned_model = FinetunedModel(eval_model, max_seq_length=max_seq_length)
        caller = finetuned_model._llm_call

        entity_extractor = EntityExtractor(llm_caller_func=caller, system_prompt=FINETUNED_ENTITIES_SYSTEM_PROMPT)
        event_extractor = EventExtractor(llm_caller_func=caller, system_prompt=FINETUNED_EVENTS_SYSTEM_PROMPT)
        argument_assigner = ArgumentAssigner(llm_caller_func=caller, system_prompt=FINETUNED_ARGUMENTS_SYSTEM_PROMPT)
        full_extractor = FullExtractor(llm_caller_func=caller, system_prompt=FINETUNED_FULL_SYSTEM_PROMPT)
    else:
        caller = make_llm_caller(eval_model)

        entity_extractor = EntityExtractor(llm_caller_func=caller, include_hints=include_hints, few_shot=few_shot)
        event_extractor = EventExtractor(llm_caller_func=caller, include_hints=include_hints, few_shot=few_shot)
        argument_assigner = ArgumentAssigner(llm_caller_func=caller, include_hints=include_hints, few_shot=few_shot)
        full_extractor = FullExtractor(llm_caller_func=caller, include_hints=include_hints, few_shot=few_shot)

    pipeline_extractor = PipelineExtractor(
        llm_caller_func=caller,
        entity_extractor=entity_extractor,
        event_extractor=event_extractor,
        argument_assigner=argument_assigner,
    )

    all_phases = [
        ("entity", EntityEvaluator(extractor=entity_extractor)),
        ("event", EventEvaluator(extractor=event_extractor)),
        ("argument", ArgumentEvaluator(assigner=argument_assigner)),
        ("pipeline", PipelineEvaluator(extractor=pipeline_extractor)),
        ("full", FullEvaluator(extractor=full_extractor)),
    ]
    selected_phases = set(phases) if phases else {name for name, _ in all_phases}
    unknown_phases = selected_phases - {name for name, _ in all_phases}
    if unknown_phases:
        raise ValueError(f"Unknown eval phase(s): {sorted(unknown_phases)}")
    phases_to_run = [(name, ev) for name, ev in all_phases if name in selected_phases]
    logger.info(f"Phases to run: {[name for name, _ in phases_to_run]}")

    results = []
    try:
        for phase, evaluator in phases_to_run:
            logger.info(f"--- Running eval phase: {phase} ---")
            start = time.time()
            precision, recall, f1 = evaluator.evaluate(dataset, sample=sample, n_jobs=n_jobs)
            duration = time.time() - start

            output_file = os.path.join(output_dir, f"{model_slug}__{phase}__{run_timestamp}.jsonl")
            _dump_predictions(evaluator, output_file)

            row = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": eval_model,
                "model_source": model_source,
                "phase": phase,
                "sample_rate": sample,
                "n_samples": n_samples,
                "options": options_label,
                "duration_seconds": round(duration, 2),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
                "output_file": output_file,
            }
            _append_csv_row(csv_path, row)
            results.append(row)
            logger.info(
                f"Phase '{phase}' done in {duration:.2f}s | "
                f"Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f} | "
                f"Predictions saved to {output_file}"
            )
    finally:
        if finetuned_model is not None:
            finetuned_model.unload()

    logger.info(f"=== Evaluation complete. Results appended to {csv_path} ===")
    return results
