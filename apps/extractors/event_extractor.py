from apps.helpers.llm_caller import call_llm_json
from apps.helpers.prompt_builder import build_events_system_prompt
from apps.models import ExtractedEvent
from apps.helpers.decorators import parallel_batch
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventExtractor:
    _instances = {}

    def __new__(cls, llm_caller_func=None, *args, **kwargs):
        if llm_caller_func not in cls._instances:
            instance = super().__new__(cls)
            instance._initialized = False
            cls._instances[llm_caller_func] = instance
        return cls._instances[llm_caller_func]

    def __init__(self, llm_caller_func=None, **kwargs):
        if llm_caller_func is not None:
            self.llm_caller_func = llm_caller_func
        if getattr(self, "_initialized", False):
            return

        self.system_prompt = build_events_system_prompt()
        if not hasattr(self, "llm_caller_func"):
            self.llm_caller_func = call_llm_json
        self._initialized = True

    @parallel_batch(max_workers=5)
    def extract(self, sentence: str) -> List[ExtractedEvent]:
        try:
            raw_answer, result = self.llm_caller_func(
                system_prompt=self.system_prompt,
                user_prompt=sentence,
                temperature=0
            )

            events = []
            for item in result.get('events', []):
                try:
                    events.append(ExtractedEvent.model_validate(item))
                except Exception:
                    pass

            logger.info(f"Raw Answer: {raw_answer}")
            logger.info(f"Events: {events}")
            return events
            
        except Exception as e:
            logger.error(e)
            return []

if __name__ == '__main__':
    extractor = EventExtractor()
    sentence = "Ông chủ Nhà Trắng hồi tháng 8/2017 ân xá cho Joe Arpaio , cảnh sát trưởng hạt Maricopa , bang Arizona , bị buộc tội không tuân lệnh toà án trong một vụ án hình sự liên quan đến những người tình nghi là dân nhập cư bất hợp pháp ."
    print("Extracting events...")
    events = extractor.extract(sentence)
    import pprint
    pprint.pprint(events)
