import logging
from typing import Tuple, Dict, Any, Union
from apps.extractors.full_extractor import FullExtractor
from apps.evaluators.metrics import Precision, Recall, F1Score
from apps.helpers.dataset_loader import load_base_dataset
from apps.models import Dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FullEvaluator:
    def __init__(self, extractor: FullExtractor = None):
        self._extractor = extractor or FullExtractor()

    @property
    def extractor(self) -> FullExtractor:
        return self._extractor

    @extractor.setter
    def extractor(self, val: FullExtractor):
        self._extractor = val

    def evaluate(self, dataset: Dataset, sample: Union[int, float] = 0.3, n_jobs: int = 1) -> Tuple[float, float, float]:
        records = dataset.items

        if isinstance(sample, float):
            sample = int(len(records) * sample)
        
        records = records[:sample]
        logger.info(f"Evaluating full extraction on {len(records)} records...")
        
        if n_jobs > 1:
            sentences = [record.sentence for record in records]
            try:
                pred_items = self.extractor.extract_batch(sentences, max_workers=n_jobs)
            except Exception as e:
                logger.error(f"Error during batch event extraction: {e}")
                pred_items = [[] for _ in sentences]
        else:
            from tqdm import tqdm
            pred_items = []
            for idx, record in enumerate(tqdm(records, desc="Evaluating")):
                try:
                    pred_items.append(self.extractor.extract(record.sentence))
                except Exception as e:
                    logger.error(f"Error extracting events for record {idx}: {e}")
                    pred_items.append([])

        self.last_sentences = [record.sentence for record in records]
        self.last_predictions = pred_items
        self.last_gold = records

        precision = Precision("full").compute(pred_items, records)
        recall = Recall("full").compute(pred_items, records)
        f1 = F1Score("full").compute(pred_items, records)

        logger.info(f"Full evaluation | n_samples: {sample} | Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")

        return precision, recall, f1

if __name__ == "__main__":
    evaluator = FullEvaluator()
    dataset = load_base_dataset("test")
    evaluator.evaluate(dataset, sample=10, n_jobs=20)
