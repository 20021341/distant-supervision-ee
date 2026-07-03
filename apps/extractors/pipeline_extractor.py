from apps.helpers.llm_caller import call_llm_json
from apps.extractors.entity_extractor import EntityExtractor
from apps.extractors.event_extractor import EventExtractor
from apps.extractors.argument_assigner import ArgumentAssigner
from apps.models import PredictedItem
from apps.helpers.decorators import parallel_batch
from typing import Optional

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PipelineExtractor:
    _instances = {}

    def __new__(cls, llm_caller_func=None, *args, **kwargs):
        if llm_caller_func not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[llm_caller_func] = instance
        return cls._instances[llm_caller_func]

    def __init__(self, llm_caller_func=None, entity_extractor=None, event_extractor=None, argument_assigner=None, **kwargs):
        if llm_caller_func is not None:
            self.llm_caller_func = llm_caller_func
        if getattr(self, "_initialized", False):
            return

        if not hasattr(self, "llm_caller_func"):
            self.llm_caller_func = call_llm_json

        self.entity_extractor = entity_extractor or EntityExtractor(llm_caller_func=self.llm_caller_func, **kwargs)
        self.event_extractor = event_extractor or EventExtractor(llm_caller_func=self.llm_caller_func, **kwargs)
        self.argument_assigner = argument_assigner or ArgumentAssigner(llm_caller_func=self.llm_caller_func, **kwargs)
        self._initialized = True

    @parallel_batch(max_workers=5)
    def extract(self, sentence: str) -> Optional[PredictedItem]:
        try:
            # 1. Extract entities
            entities = self.entity_extractor.extract(sentence)
            
            # 2. Extract events
            events = self.event_extractor.extract(sentence)
            
            # 3. Assign arguments to each event
            assigned_events = []
            for event in events:
                try:
                    assigned_event = self.argument_assigner.assign(sentence, event, entities)
                    if assigned_event is not None:
                        assigned_events.append(assigned_event)
                except Exception as e:
                    logger.error(f"Error assigning arguments for event {event}: {e}")
            
            logger.info(f"Pipeline Entities: {entities}")
            logger.info(f"Pipeline Events: {assigned_events}")
            return PredictedItem(entities=entities, events=assigned_events)
        except Exception as e:
            logger.error(e)
            return None


if __name__ == '__main__':
    extractor = PipelineExtractor()
    sentence = "Ông chủ Nhà Trắng hồi tháng 8/2017 ân xá cho Joe Arpaio , cảnh sát trưởng hạt Maricopa , bang Arizona , bị buộc tội không tuân lệnh toà án trong một vụ án hình sự liên quan đến những người tình nghi là dân nhập cư bất hợp pháp ."
    logger.info(extractor.extract(sentence))
