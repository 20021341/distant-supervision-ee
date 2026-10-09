import os
import csv
import glob
import json
import re
import time
import logging
from datetime import datetime, timezone
from typing import List, Tuple, Union, Dict, Any, Optional

from pydantic import BaseModel

from apps.helpers.dataset_loader import load_base_dataset
from apps.helpers.llm_caller import make_llm_caller
from apps.models import ExtractedEntity, ExtractedEvent
from apps.constants import (
    FINETUNED_ENTITIES_SYSTEM_PROMPT,
    FINETUNED_EVENTS_SYSTEM_PROMPT,
    FINETUNED_ARGUMENTS_SYSTEM_PROMPT,
    FINETUNED_FULL_SYSTEM_PROMPT,
    MODEL_PRESETS,
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

# Each preset fully determines which system prompt to use, independent of where the
# model is loaded from (local checkpoint path, served endpoint, or OpenRouter id).
PROMPT_PRESETS: Dict[str, Dict[str, bool]] = {
    "finetuned": {"fixed": True, "include_hints": False, "few_shot": False},
    "instruction": {"fixed": False, "include_hints": False, "few_shot": False},
    "instruction,type_hints": {"fixed": False, "include_hints": True, "few_shot": False},
    "instruction,type_hints,few_shot": {"fixed": False, "include_hints": True, "few_shot": True},
}

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


def _dump_rows(sentences: List[str], predictions: List[Any], gold: Optional[List[Any]], output_path: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for i in range(len(predictions)):
            row = {
                "sentence": sentences[i] if i < len(sentences) else None,
                "prediction": _to_jsonable(predictions[i]),
                "gold": _to_jsonable(gold[i]) if (gold and i < len(gold)) else None,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _dump_predictions(evaluator: Any, output_path: str) -> None:
    sentences = getattr(evaluator, "last_sentences", [])
    predictions = getattr(evaluator, "last_predictions", [])
    gold = getattr(evaluator, "last_gold", [])
    _dump_rows(sentences, predictions, gold, output_path)


def _find_latest_output_file(output_dir: str, model_slug: str, phase: str) -> Optional[str]:
    """
    Looks for a previously-dumped prediction file for this model+phase, e.g. from an
    earlier standalone `--eval_phases entity` run. Filenames are timestamp-suffixed
    (`{model_slug}__{phase}__{run_timestamp}.jsonl`), so a plain sort picks the latest.
    """
    pattern = os.path.join(output_dir, f"{model_slug}__{phase}__*.jsonl")
    matches = sorted(glob.glob(pattern))
    return matches[-1] if matches else None


def _load_phase_predictions_from_file(path: str, phase: str) -> Tuple[List[str], List[List[Any]]]:
    item_cls = ExtractedEntity if phase == "entity" else ExtractedEvent
    sentences = []
    predictions = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            sentences.append(row.get("sentence"))
            items = []
            for d in (row.get("prediction") or []):
                try:
                    items.append(item_cls.model_validate(d))
                except Exception:
                    pass
            predictions.append(items)
    return sentences, predictions


def _try_reuse_entity_event_predictions(
    output_dir: str, model_slug: str, current_sentences: List[str]
) -> Tuple[Optional[List[List[ExtractedEntity]]], Optional[List[List[ExtractedEvent]]]]:
    """
    Looks for previously-saved entity and event phase output files for this model
    (e.g. from an earlier `--eval_phases entity event` run) and reuses them for the
    pipeline phase if their sentences line up exactly with the current sample --
    avoids re-paying for entity/event LLM calls that already happened.
    """
    entity_file = _find_latest_output_file(output_dir, model_slug, "entity")
    event_file = _find_latest_output_file(output_dir, model_slug, "event")
    if not entity_file or not event_file:
        return None, None

    entity_sentences, entity_predictions = _load_phase_predictions_from_file(entity_file, "entity")
    event_sentences, event_predictions = _load_phase_predictions_from_file(event_file, "event")

    if entity_sentences != current_sentences or event_sentences != current_sentences:
        logger.info(
            "Found cached entity/event output files but their sentences don't match the "
            "current sample (different --sample or dataset order) -- recomputing from scratch."
        )
        return None, None

    logger.info(f"Reusing cached entity predictions from {entity_file}")
    logger.info(f"Reusing cached event predictions from {event_file}")
    return entity_predictions, event_predictions


def _append_csv_row(csv_path: str, row: Dict[str, Any]) -> None:
    parent_dir = os.path.dirname(os.path.abspath(csv_path))
    os.makedirs(parent_dir, exist_ok=True)
    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def _resolve_checkpoint_path(path: str) -> str:
    if os.path.exists(path):
        return path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    candidate = os.path.join(project_root, path)
    if os.path.exists(candidate):
        return candidate
    alt1 = os.path.join(path, "final")
    if os.path.exists(alt1):
        return alt1
    alt2 = os.path.join(candidate, "final")
    if os.path.exists(alt2):
        return alt2
    return path


def _create_caller(
    model_name_or_path: str,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
    max_seq_length: int = 2048,
) -> Tuple[Any, Optional[Any], str]:
    """
    Returns (caller, finetuned_model_instance, model_source).
    If local checkpoint, finetuned_model_instance is returned so caller can manage its lifecycle/unload.
    """
    is_served = base_url is not None
    resolved_path = _resolve_checkpoint_path(model_name_or_path)
    is_local = (not is_served) and os.path.exists(resolved_path)
    model_source = "vllm" if is_served else ("local_checkpoint" if is_local else "openrouter")

    finetuned_model = None
    if is_served:
        caller = make_llm_caller(model_name_or_path, base_url=base_url, api_key=api_key)
    elif is_local:
        from apps.trainers.inference_models import FinetunedModel
        finetuned_model = FinetunedModel(resolved_path, max_seq_length=max_seq_length)
        caller = finetuned_model._llm_call
    else:
        caller = make_llm_caller(model_name_or_path)

    return caller, finetuned_model, model_source


def _build_extractor(
    phase: str,
    caller: Any,
    use_fixed_prompt: bool,
    include_hints: bool,
    few_shot: bool,
) -> Any:
    if phase == "entity":
        if use_fixed_prompt:
            return EntityExtractor(llm_caller_func=caller, system_prompt=FINETUNED_ENTITIES_SYSTEM_PROMPT)
        return EntityExtractor(llm_caller_func=caller, include_hints=include_hints, few_shot=few_shot)
    elif phase == "event":
        if use_fixed_prompt:
            return EventExtractor(llm_caller_func=caller, system_prompt=FINETUNED_EVENTS_SYSTEM_PROMPT)
        return EventExtractor(llm_caller_func=caller, include_hints=include_hints, few_shot=few_shot)
    elif phase == "argument":
        if use_fixed_prompt:
            return ArgumentAssigner(llm_caller_func=caller, system_prompt=FINETUNED_ARGUMENTS_SYSTEM_PROMPT)
        return ArgumentAssigner(llm_caller_func=caller, include_hints=include_hints, few_shot=few_shot)
    elif phase == "full":
        if use_fixed_prompt:
            return FullExtractor(llm_caller_func=caller, system_prompt=FINETUNED_FULL_SYSTEM_PROMPT)
        return FullExtractor(llm_caller_func=caller, include_hints=include_hints, few_shot=few_shot)
    raise ValueError(f"Unknown phase for extractor: {phase}")


def _build_evaluator(phase: str, extractor_or_assigner: Any) -> Any:
    if phase == "entity":
        return EntityEvaluator(extractor=extractor_or_assigner)
    elif phase == "event":
        return EventEvaluator(extractor=extractor_or_assigner)
    elif phase == "argument":
        return ArgumentEvaluator(assigner=extractor_or_assigner)
    elif phase == "pipeline":
        return PipelineEvaluator(extractor=extractor_or_assigner)
    elif phase == "full":
        return FullEvaluator(extractor=extractor_or_assigner)
    raise ValueError(f"Unknown phase for evaluator: {phase}")


def _extract_pipeline_subphase(
    subphase: str,
    model_name_or_path: str,
    records: List[Any],
    base_url: Optional[str],
    api_key: Optional[str],
    max_seq_length: int,
    use_fixed_prompt: bool,
    include_hints: bool,
    few_shot: bool,
    n_jobs: int,
) -> List[Any]:
    caller, ft_model, _ = _create_caller(
        model_name_or_path, base_url=base_url, api_key=api_key, max_seq_length=max_seq_length
    )
    try:
        extractor = _build_extractor(subphase, caller, use_fixed_prompt, include_hints, few_shot)
        sentences = [r.sentence for r in records]
        effective_n_jobs = 1 if ft_model is not None else n_jobs
        if effective_n_jobs > 1:
            return extractor.extract_batch(sentences, max_workers=effective_n_jobs)
        else:
            from tqdm import tqdm
            preds = []
            for s in tqdm(sentences, desc=f"Pipeline: extracting {subphase}s"):
                preds.append(extractor.extract(s))
            return preds
    finally:
        if ft_model is not None:
            ft_model.unload()


def run_evaluation(
    eval_model: str,
    sample: Union[int, float] = 1.0,
    n_jobs: int = 5,
    prompt: str = "finetuned",
    csv_path: str = "eval_results.csv",
    output_dir: str = "eval_outputs",
    max_seq_length: int = 2048,
    phases: Optional[List[str]] = None,
    base_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Runs entity, event, argument, pipeline (entity -> event -> argument) and
    full (single-call) evaluation on the test split for the given model/preset, then
    appends one CSV row per phase to `csv_path` and dumps raw predictions for
    each phase to a JSONL file under `output_dir`.

    `eval_model` can be:
      - A preset name defined in `MODEL_PRESETS` (e.g. "finetuned"), which automatically
        maps to task-specific checkpoints (entity, event, argument, full).
      - An existing local checkpoint path.
      - A model identifier to call over network via `base_url` (vLLM) or OpenRouter.

    `phases`: subset of {"entity", "event", "argument", "pipeline", "full"} to run.
    Defaults to all five when omitted/empty.
    """
    if prompt not in PROMPT_PRESETS:
        raise ValueError(f"Unknown prompt preset {prompt!r}; choose from {sorted(PROMPT_PRESETS)}")
    preset = PROMPT_PRESETS[prompt]
    use_fixed_prompt, include_hints, few_shot = preset["fixed"], preset["include_hints"], preset["few_shot"]

    is_preset = eval_model in MODEL_PRESETS
    preset_mapping = MODEL_PRESETS[eval_model] if is_preset else None

    is_served = base_url is not None
    if is_preset:
        model_source = "vllm" if is_served else "local_checkpoint"
        logger.info(f"=== Starting evaluation for preset: {eval_model} ({model_source}), prompt: {prompt} ===")
        logger.info(f"Preset checkpoint mapping: {preset_mapping}")
    else:
        is_local = (not is_served) and os.path.exists(_resolve_checkpoint_path(eval_model))
        model_source = "vllm" if is_served else ("local_checkpoint" if is_local else "openrouter")
        logger.info(f"=== Starting evaluation for model: {eval_model} ({model_source}), prompt: {prompt} ===")

    dataset = load_base_dataset("test")
    n_records = len(dataset.items)
    n_samples = int(n_records * sample) if isinstance(sample, float) else min(sample, n_records)

    run_timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    # Suffixing with the prompt preset keeps output files (and the pipeline-phase
    # entity/event prediction cache below) scoped per prompt variant, so runs with
    # different presets for the same model never collide or get reused across each other.
    base_model_slug = _slugify(os.path.basename(eval_model.rstrip("/\\")) or eval_model)
    model_slug = f"{base_model_slug}__{_slugify(prompt)}"

    all_phase_names = ["entity", "event", "argument", "pipeline", "full"]
    selected_phases = set(phases) if phases else set(all_phase_names)
    unknown_phases = selected_phases - set(all_phase_names)
    if unknown_phases:
        raise ValueError(f"Unknown eval phase(s): {sorted(unknown_phases)}")
    phases_to_run = [name for name in all_phase_names if name in selected_phases]
    logger.info(f"Phases to run: {phases_to_run}")

    results = []
    entity_predictions = None
    event_predictions = None

    if is_preset:
        for phase in phases_to_run:
            logger.info(f"--- Running eval phase: {phase} (Preset: {eval_model}) ---")
            start = time.time()
            evaluator = None
            phase_source = model_source

            if phase == "pipeline":
                current_sentences = [record.sentence for record in dataset.items[:n_samples]]
                if entity_predictions is None or event_predictions is None:
                    cached_ent, cached_ev = _try_reuse_entity_event_predictions(
                        output_dir, model_slug, current_sentences
                    )
                    if entity_predictions is None:
                        entity_predictions = cached_ent
                    if event_predictions is None:
                        event_predictions = cached_ev

                if entity_predictions is None:
                    ent_target = preset_mapping["entity"]
                    logger.info(f"Pipeline requires entity extraction: using preset entity checkpoint '{ent_target}'...")
                    entity_predictions = _extract_pipeline_subphase(
                        "entity", ent_target, dataset.items[:n_samples],
                        base_url, api_key, max_seq_length, use_fixed_prompt, include_hints, few_shot, n_jobs
                    )
                    ent_cache_file = os.path.join(output_dir, f"{model_slug}__entity__{run_timestamp}.jsonl")
                    _dump_rows(current_sentences, entity_predictions, [r.entities for r in dataset.items[:n_samples]], ent_cache_file)

                if event_predictions is None:
                    ev_target = preset_mapping["event"]
                    logger.info(f"Pipeline requires event extraction: using preset event checkpoint '{ev_target}'...")
                    event_predictions = _extract_pipeline_subphase(
                        "event", ev_target, dataset.items[:n_samples],
                        base_url, api_key, max_seq_length, use_fixed_prompt, include_hints, few_shot, n_jobs
                    )
                    ev_cache_file = os.path.join(output_dir, f"{model_slug}__event__{run_timestamp}.jsonl")
                    _dump_rows(current_sentences, event_predictions, [r.events for r in dataset.items[:n_samples]], ev_cache_file)

                arg_target = preset_mapping["argument"]
                logger.info(f"Pipeline running argument assignment with preset checkpoint: '{arg_target}'...")
                arg_caller, arg_ft_model, phase_source = _create_caller(
                    arg_target, base_url=base_url, api_key=api_key, max_seq_length=max_seq_length
                )
                try:
                    arg_assigner = _build_extractor("argument", arg_caller, use_fixed_prompt, include_hints, few_shot)
                    pipeline_extractor = PipelineExtractor(argument_assigner=arg_assigner)
                    pipeline_extractor.argument_assigner = arg_assigner
                    evaluator = PipelineEvaluator(extractor=pipeline_extractor)
                    effective_n_jobs = 1 if arg_ft_model is not None else n_jobs
                    precision, recall, f1 = evaluator.evaluate(
                        dataset,
                        sample=sample,
                        n_jobs=effective_n_jobs,
                        precomputed_entities=entity_predictions,
                        precomputed_events=event_predictions,
                    )
                finally:
                    if arg_ft_model is not None:
                        arg_ft_model.unload()

            else:
                task_target = preset_mapping[phase]
                logger.info(f"Phase '{phase}' running with preset checkpoint: '{task_target}'...")
                phase_caller, phase_ft_model, phase_source = _create_caller(
                    task_target, base_url=base_url, api_key=api_key, max_seq_length=max_seq_length
                )
                try:
                    extractor = _build_extractor(phase, phase_caller, use_fixed_prompt, include_hints, few_shot)
                    evaluator = _build_evaluator(phase, extractor)
                    effective_n_jobs = 1 if phase_ft_model is not None else n_jobs
                    precision, recall, f1 = evaluator.evaluate(dataset, sample=sample, n_jobs=effective_n_jobs)
                    if phase == "entity":
                        entity_predictions = evaluator.last_predictions
                    elif phase == "event":
                        event_predictions = evaluator.last_predictions
                finally:
                    if phase_ft_model is not None:
                        phase_ft_model.unload()

            duration = time.time() - start
            output_file = os.path.join(output_dir, f"{model_slug}__{phase}__{run_timestamp}.jsonl")
            _dump_predictions(evaluator, output_file)

            row = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "model": eval_model,
                "model_source": phase_source,
                "phase": phase,
                "sample_rate": sample,
                "n_samples": n_samples,
                "options": prompt,
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

    else:
        # Non-preset flow: single model evaluated across all selected phases
        caller, finetuned_model, model_source = _create_caller(
            eval_model, base_url=base_url, api_key=api_key, max_seq_length=max_seq_length
        )
        try:
            if finetuned_model is not None and n_jobs != 1:
                logger.warning("Local checkpoint inference is not thread-safe; forcing n_jobs=1.")
                n_jobs = 1

            entity_extractor = _build_extractor("entity", caller, use_fixed_prompt, include_hints, few_shot)
            event_extractor = _build_extractor("event", caller, use_fixed_prompt, include_hints, few_shot)
            argument_assigner = _build_extractor("argument", caller, use_fixed_prompt, include_hints, few_shot)
            full_extractor = _build_extractor("full", caller, use_fixed_prompt, include_hints, few_shot)
            pipeline_extractor = PipelineExtractor(
                llm_caller_func=caller,
                entity_extractor=entity_extractor,
                event_extractor=event_extractor,
                argument_assigner=argument_assigner,
            )
            pipeline_extractor.entity_extractor = entity_extractor
            pipeline_extractor.event_extractor = event_extractor
            pipeline_extractor.argument_assigner = argument_assigner

            all_evaluators = {
                "entity": EntityEvaluator(extractor=entity_extractor),
                "event": EventEvaluator(extractor=event_extractor),
                "argument": ArgumentEvaluator(assigner=argument_assigner),
                "pipeline": PipelineEvaluator(extractor=pipeline_extractor),
                "full": FullEvaluator(extractor=full_extractor),
            }

            for phase in phases_to_run:
                evaluator = all_evaluators[phase]
                logger.info(f"--- Running eval phase: {phase} ---")
                start = time.time()

                if phase == "pipeline" and (entity_predictions is None or event_predictions is None):
                    current_sentences = [record.sentence for record in dataset.items[:n_samples]]
                    entity_predictions, event_predictions = _try_reuse_entity_event_predictions(
                        output_dir, model_slug, current_sentences
                    )

                if phase == "pipeline" and entity_predictions is not None and event_predictions is not None:
                    precision, recall, f1 = evaluator.evaluate(
                        dataset,
                        sample=sample,
                        n_jobs=n_jobs,
                        precomputed_entities=entity_predictions,
                        precomputed_events=event_predictions,
                    )
                else:
                    precision, recall, f1 = evaluator.evaluate(dataset, sample=sample, n_jobs=n_jobs)
                duration = time.time() - start

                if phase == "entity":
                    entity_predictions = evaluator.last_predictions
                elif phase == "event":
                    event_predictions = evaluator.last_predictions

                output_file = os.path.join(output_dir, f"{model_slug}__{phase}__{run_timestamp}.jsonl")
                _dump_predictions(evaluator, output_file)

                row = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "model": eval_model,
                    "model_source": model_source,
                    "phase": phase,
                    "sample_rate": sample,
                    "n_samples": n_samples,
                    "options": prompt,
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
