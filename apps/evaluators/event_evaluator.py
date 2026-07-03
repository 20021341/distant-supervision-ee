import logging
from typing import Tuple, Dict, Any, Union
from apps.extractors.event_extractor import EventExtractor
from apps.evaluators.metrics import Precision, Recall, F1Score
from apps.helpers.dataset_loader import load_base_dataset
from apps.models import Dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventEvaluator:
    def __init__(self, extractor: EventExtractor = None):
        self._extractor = extractor or EventExtractor()

    @property
    def extractor(self) -> EventExtractor:
        return self._extractor

    @extractor.setter
    def extractor(self, val: EventExtractor):
        self._extractor = val

    def evaluate(self, dataset: Dataset, sample: Union[int, float] = 0.3, n_jobs: int = 1) -> Tuple[float, float, float]:
        records = dataset.items

        if isinstance(sample, float):
            sample = int(len(records) * sample)
        
        records = records[:sample]
        logger.info(f"Evaluating event extraction on {len(records)} records...")
        
        if n_jobs > 1:
            sentences = [record.sentence for record in records]
            try:
                pred_events_list = self.extractor.extract_batch(sentences, max_workers=n_jobs)
            except Exception as e:
                logger.error(f"Error during batch event extraction: {e}")
                pred_events_list = [[] for _ in sentences]
        else:
            pred_events_list = []
            for idx, record in enumerate(records):
                try:
                    pred_events_list.append(self.extractor.extract(record.sentence))
                except Exception as e:
                    logger.error(f"Error extracting events for record {idx}: {e}")
                    pred_events_list.append([])

        pred_list = pred_events_list
        gold_list = [record.events for record in records]

        precision = Precision("event").compute(pred_list, gold_list)
        recall = Recall("event").compute(pred_list, gold_list)
        f1 = F1Score("event").compute(pred_list, gold_list)

        logger.info(f"Event evaluation | n_samples: {sample} | Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")

        return precision, recall, f1

if __name__ == "__main__":
    evaluator = EventEvaluator()
    dataset = load_base_dataset("test")
    evaluator.evaluate(dataset, sample=10, n_jobs=20)
