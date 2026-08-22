import logging
from typing import Tuple, Union
from apps.extractors.entity_extractor import EntityExtractor
from apps.evaluators.metrics import Precision, Recall, F1Score
from apps.helpers.dataset_loader import load_base_dataset
from apps.models import Dataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EntityEvaluator:
    def __init__(self, extractor: EntityExtractor = None):
        self._extractor = extractor or EntityExtractor()

    @property
    def extractor(self) -> EntityExtractor:
        return self._extractor

    @extractor.setter
    def extractor(self, val: EntityExtractor):
        self._extractor = val

    def evaluate(self, dataset: Dataset, sample: Union[int, float] = 0.3, n_jobs: int = 1) -> Tuple[float, float, float]:
        records = dataset.items

        if isinstance(sample, float):
            sample = int(len(records) * sample)
        
        records = records[:sample]
        logger.info(f"Evaluating entity extraction on {len(records)} records...")
        
        if n_jobs > 1:
            sentences = [record.sentence for record in records]
            try:
                pred_entities_list = self.extractor.extract_batch(sentences, max_workers=n_jobs)
            except Exception as e:
                logger.error(f"Error during batch entity extraction: {e}")
                pred_entities_list = [[] for _ in sentences]
        else:
            from tqdm import tqdm
            pred_entities_list = []
            for idx, record in enumerate(tqdm(records, desc="Evaluating")):
                try:
                    pred_entities_list.append(self.extractor.extract(record.sentence))
                except Exception as e:
                    logger.error(f"Error extracting entities for record {idx}: {e}")
                    pred_entities_list.append([])

        pred_list = pred_entities_list
        gold_list = [record.entities for record in records]

        self.last_sentences = [record.sentence for record in records]
        self.last_predictions = pred_list
        self.last_gold = gold_list

        precision = Precision("entity").compute(pred_list, gold_list)
        recall = Recall("entity").compute(pred_list, gold_list)
        f1 = F1Score("entity").compute(pred_list, gold_list)
        logger.info(f"Entity evaluation | n_samples: {sample} | Precision: {precision:.4f}, Recall: {recall:.4f}, F1: {f1:.4f}")

        return precision, recall, f1

if __name__ == "__main__":
    evaluator = EntityEvaluator()
    dataset = load_base_dataset("test")
    evaluator.evaluate(dataset, sample=10, n_jobs=20)
