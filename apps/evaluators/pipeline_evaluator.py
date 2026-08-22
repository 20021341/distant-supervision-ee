import logging
from typing import Tuple, Union
from apps.extractors.pipeline_extractor import PipelineExtractor
from apps.evaluators.metrics import Precision, Recall, F1Score
from apps.helpers.dataset_loader import load_base_dataset
from apps.models import Dataset

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

    def evaluate(self, dataset: Dataset, sample: Union[int, float] = 0.3, n_jobs: int = 1) -> Tuple[float, float, float]:
        records = dataset.items

        if isinstance(sample, float):
            sample = int(len(records) * sample)
        
        records = records[:sample]
        logger.info(f"Evaluating pipeline extraction on {len(records)} records...")
        
        if n_jobs > 1:
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
