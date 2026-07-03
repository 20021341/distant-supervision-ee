from typing import Any, Dict, List, Tuple, Literal, Union, Optional
from apps.models import ExtractedEntity, ExtractedEvent, AssignedEvent, MentionedEntity, MentionedEvent, PredictedItem, DatasetItem
from apps.helpers.text_processing import is_similar_text
import itertools

def _compute_tp_fp_fn_values(
    prediction: Any, 
    gold: Any, 
    phase: Literal["entity", "event", "argument", "full"]
) -> Tuple[float, float, float]:
    """
    Computes true positives (tp), false positives (fp), and false negatives (fn)
    for a single record/sentence under the given phase, returning (tp, fp, fn).
    Uses strict type hinting and direct model property accesses (no hasattr/getattr).
    """
    if phase == "entity":
        prediction: List[ExtractedEntity] = prediction
        gold: List[MentionedEntity] = gold

        tp = 0
        matched_gold_indices = set()
        for p in prediction:
            p_text = p.text
            p_type = p.type
            
            matched = False
            for g_idx, g in enumerate(gold):
                if g_idx in matched_gold_indices:
                    continue
                g_text = g.text
                g_type = g.type
                
                if str(p_type).lower() == str(g_type).lower() and is_similar_text(p_text, g_text):
                    tp += 1
                    matched_gold_indices.add(g_idx)
                    matched = True
                    break
        
        fp = len(prediction) - tp
        fn = len(gold) - tp
        return float(tp), float(fp), float(fn)

    elif phase == "event":
        prediction: List[ExtractedEvent] = prediction
        gold: List[MentionedEvent] = gold

        tp = 0
        matched_gold_indices = set()
        for p in prediction:
            p_trig = p.trigger
            p_type = p.type

            matched = False
            for g_idx, g in enumerate(gold):
                if g_idx in matched_gold_indices:
                    continue
                g_trig = g.trigger
                g_type = g.type

                if str(p_type).lower() == str(g_type).lower() and is_similar_text(p_trig, g_trig):
                    tp += 1
                    matched_gold_indices.add(g_idx)
                    matched = True
                    break

        fp = len(prediction) - tp
        fn = len(gold) - tp
        return float(tp), float(fp), float(fn)

    elif phase == "argument":
        prediction: AssignedEvent = prediction
        gold: MentionedEvent = gold

        tp = 0
        fp = 0
        fn = 0
            
        pred_args = prediction.arguments if prediction is not None else []
        gold_args = gold.arguments

        matched_gold_indices = set()
        for p in pred_args:
            p_text = p.text
            p_role = p.type

            matched = False
            for g_idx, g in enumerate(gold_args):
                if g_idx in matched_gold_indices:
                    continue
                g_text = g.text
                g_role = g.type

                if str(p_role).lower() == str(g_role).lower() and is_similar_text(p_text, g_text):
                    tp += 1
                    matched_gold_indices.add(g_idx)
                    matched = True
                    break
            if not matched:
                fp += 1

        fn += len(gold_args) - len(matched_gold_indices)

        return float(tp), float(fp), float(fn)

    else:
        prediction: PredictedItem = prediction
        gold: DatasetItem = gold

        # Guard: extractor may return None on failure
        if prediction is None:
            pred_ents, pred_events = [], []
        else:
            pred_ents, pred_events = prediction.entities, prediction.events
        gold_ents, gold_events = gold.entities, gold.events

        tp_ents, fp_ents, fn_ents = _compute_tp_fp_fn_values(pred_ents, gold_ents, "entity")

        pred_extracted_events = [ExtractedEvent(trigger=ev.trigger, type=ev.type) for ev in pred_events if ev is not None]
        tp_events, fp_events, fn_events = _compute_tp_fp_fn_values(pred_extracted_events, gold_events, "event")

        tp_args, fp_args, fn_args = 0, 0, 0
        for pred_event, gold_event in zip(pred_events, gold_events):
            _tp, _fp, _fn = _compute_tp_fp_fn_values(pred_event, gold_event, "argument")
            tp_args += _tp
            fp_args += _fp
            fn_args += _fn

        # Combine EMD, ED, and EAE counts
        tp_total = tp_ents + tp_events + tp_args
        fp_total = fp_ents + fp_events + fp_args
        fn_total = fn_ents + fn_events + fn_args
        return float(tp_total), float(fp_total), float(fn_total)


def compute_metrics(
    predictions: List[Any],
    gold_data: List[Any],
    phase: Literal["entity", "event", "argument", "full"],
) -> Tuple[float, float, float]:
    """
    Tính Precision, Recall và F1 trong một lần duyệt duy nhất.

    Returns:
        (precision, recall, f1)
    """
    tp_total, fp_total, fn_total = 0.0, 0.0, 0.0
    for p, g in zip(predictions, gold_data):
        tp, fp, fn = _compute_tp_fp_fn_values(p, g, phase)
        tp_total += tp
        fp_total += fp
        fn_total += fn

    precision = tp_total / (tp_total + fp_total) if (tp_total + fp_total) > 0.0 else 0.0
    recall    = tp_total / (tp_total + fn_total) if (tp_total + fn_total) > 0.0 else 0.0
    f1        = 2.0 * precision * recall / (precision + recall) if (precision + recall) > 0.0 else 0.0
    return precision, recall, f1


class Precision:
    def __init__(self, phase: Literal["entity", "event", "argument", "full"]):
        self.phase = phase

    def compute(self, predictions: List[Any], gold_data: List[Any]) -> float:
        precision, _, _ = compute_metrics(predictions, gold_data, self.phase)
        return precision


class Recall:
    def __init__(self, phase: Literal["entity", "event", "argument", "full"]):
        self.phase = phase

    def compute(self, predictions: List[Any], gold_data: List[Any]) -> float:
        _, recall, _ = compute_metrics(predictions, gold_data, self.phase)
        return recall


class F1Score:
    def __init__(self, phase: Literal["entity", "event", "argument", "full"]):
        self.phase = phase

    def compute(self, predictions: List[Any], gold_data: List[Any]) -> float:
        _, _, f1 = compute_metrics(predictions, gold_data, self.phase)
        return f1
