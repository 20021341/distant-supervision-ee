import logging
from typing import List, Optional, Tuple, Union
from apps.extractors.pipeline_extractor import PipelineExtractor
from apps.evaluators.metrics import Precision, Recall, F1Score
from apps.helpers.dataset_loader import load_base_dataset
from apps.models import Dataset, ExtractedEntity, ExtractedEvent, PredictedItem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineEvaluator:
    def __init__(self, extractor: PipelineExtractor = None):
        self._extractor = extractor or PipelineExtractor()

    @property
    def extractor(self) -> PipelineExtractor:
        return self._extractor

    @extractor.setter
    def extractor(self, val: PipelineExtractor):
        self._extractor = val

    def _assign_arguments_only(
        self,
        records,
        entities_list: List[List[ExtractedEntity]],
        events_list: List[List[ExtractedEvent]],
        n_jobs: int,
    ) -> List[Optional[PredictedItem]]:
        """
        Skips entity/event LLM extraction and reuses already-computed entities/events
        (e.g. from the entity and event eval phases run earlier in the same eval run),
        only calling the argument assigner -- avoids paying for redundant entity/event
        LLM calls when pipeline is evaluated right after those two phases.
        """
        assigner = self.extractor.argument_assigner

        flat_tasks = []
        task_owner = []
        for rec_idx, (record, events) in enumerate(zip(records, events_list)):
            entities = entities_list[rec_idx]
            for event in events:
                flat_tasks.append((record.sentence, event, entities))
                task_owner.append(rec_idx)

        if n_jobs > 1 and flat_tasks:
            try:
                flat_results = assigner.assign_batch(flat_tasks, max_workers=n_jobs)
            except Exception as e:
                logger.error(f"Error during batch argument assignment for pipeline reuse: {e}")
                flat_results = [None for _ in flat_tasks]
        else:
            flat_results = []
            for sentence, event, entities in flat_tasks:
                try:
                    flat_results.append(assigner.assign(sentence, event, entities))
                except Exception as e:
                    logger.error(f"Error assigning arguments for pipeline reuse: {e}")
                    flat_results.append(None)

        assigned_by_record = [[] for _ in records]
        for owner_idx, assigned_event in zip(task_owner, flat_results):
            if assigned_event is not None:
                assigned_by_record[owner_idx].append(assigned_event)

        return [
            PredictedItem(entities=entities_list[i], events=assigned_by_record[i])
            for i in range(len(records))
        ]

    def evaluate(
        self,
        dataset: Dataset,
        sample: Union[int, float] = 0.3,
        n_jobs: int = 1,
        precomputed_entities: Optional[List[List[ExtractedEntity]]] = None,
        precomputed_events: Optional[List[List[ExtractedEvent]]] = None,
    ) -> Tuple[float, float, float]:
        records = dataset.items

        if isinstance(sample, float):
            sample = int(len(records) * sample)

        records = records[:sample]
        logger.info(f"Evaluating pipeline extraction on {len(records)} records...")

        if precomputed_entities is not None and precomputed_events is not None:
            logger.info("Reusing precomputed entity/event predictions for pipeline eval (skipping entity/event LLM calls).")
            pred_items = self._assign_arguments_only(records, precomputed_entities, precomputed_events, n_jobs)
        elif n_jobs > 1:
            sentences = [record.sentence for record in records]
            try:
                pred_items = self.extractor.extract_batch(sentences, max_workers=n_jobs)
            except Exception as e:
                logger.error(f"Error during batch pipeline extraction: {e}")
                pred_items = [None for _ in sentences]
        else:
            pred_items = []
            for idx, record in enumerate(records):
                try:
                    pred_items.append(self.extractor.extract(record.sentence))
                except Exception as e:
                    logger.error(f"Error pipeline-extracting for record {idx}: {e}")
                    pred_items.append(None)

        self.last_sentences = [record.sentence for record in records]
        self.last_predictions = pred_items
        self.last_gold = records

        precision = Precision("full").compute(pred_items, records)
        recall = Recall("full").compute(pred_items, records)
        f1 = F1Score("full").compute(pred_items, records)

        logger.info(f"Pipeline evaluation | n_samples: {sample} | Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")

        return precision, recall, f1

if __name__ == "__main__":
    evaluator = PipelineEvaluator()
    dataset = load_base_dataset("test")
    evaluator.evaluate(dataset, sample=10, n_jobs=20)
