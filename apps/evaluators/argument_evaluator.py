import logging
from typing import Tuple, Dict, Any, Union
from apps.extractors.argument_assigner import ArgumentAssigner
from apps.evaluators.metrics import Precision, Recall, F1Score
from apps.helpers.dataset_loader import load_base_dataset
from apps.models import Dataset, ExtractedEntity, ExtractedEvent
import itertools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ArgumentEvaluator:
    def __init__(self, assigner: ArgumentAssigner = None):
        self._assigner = assigner or ArgumentAssigner()

    @property
    def assigner(self) -> ArgumentAssigner:
        return self._assigner

    @assigner.setter
    def assigner(self, val: ArgumentAssigner):
        self._assigner = val

    def evaluate(self, dataset: Dataset, sample: Union[int, float] = 0.3, n_jobs: int = 1) -> Tuple[float, float, float]:
        records = dataset.items

        if isinstance(sample, float):
            sample = int(len(records) * sample)
        
        records = records[:sample]
        logger.info(f"Evaluating argument assignment on {len(records)} records...")
        
        # Collect all tasks to run in batch
        tasks = []

        for idx, record in enumerate(records):
            sentence = record.sentence
            gold_events = record.events
            gold_entities = record.entities

            if not gold_events or not gold_entities:
                continue

            # Format candidate entities to match extractor interface
            candidate_entities = [
                ExtractedEntity(text=entity.text, type=entity.type)
                for entity in gold_entities
            ]

            for event in gold_events:
                event_input = ExtractedEvent(
                    type=event.type,
                    trigger=event.trigger
                )
                tasks.append((sentence, event_input, candidate_entities))

        if not tasks:
            logger.info("No argument assignment tasks found to evaluate.")
            return 0.0, 0.0, 0.0

        if n_jobs > 1:
            try:
                pred_events = self.assigner.assign_batch(tasks, max_workers=n_jobs)
            except Exception as e:
                logger.error(f"Error during batch argument assignment: {e}")
                pred_events = [None for _ in tasks]
        else:
            pred_events = []
            for task in tasks:
                sentence, event_input, candidate_entities = task
                try:
                    pred_events.append(self.assigner.assign(sentence, event_input, candidate_entities))
                except Exception as e:
                    logger.error(f"Error assigning arguments for event {event_input}: {e}")
                    pred_events.append(None)

        gold_events = list(itertools.chain(*[record.events for record in records]))

        precision = Precision("argument").compute(pred_events, gold_events)
        recall = Recall("argument").compute(pred_events, gold_events)
        f1 = F1Score("argument").compute(pred_events, gold_events)

        logger.info(f"Argument evaluation | n_samples: {sample} | Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")

        return precision, recall, f1

if __name__ == "__main__":
    evaluator = ArgumentEvaluator()
    dataset = load_base_dataset("test")
    evaluator.evaluate(dataset, sample=10, n_jobs=20)
