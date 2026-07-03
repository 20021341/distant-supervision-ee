from apps.helpers.llm_caller import call_llm_json
from apps.helpers.prompt_builder import build_arguments_system_prompt, build_arguments_user_prompt
from apps.models import ExtractedEntity, ExtractedEvent, Argument, AssignedEvent
from apps.helpers.decorators import parallel_batch
from typing import List, Optional
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArgumentAssigner:
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

        self.system_prompt = build_arguments_system_prompt()
        if not hasattr(self, "llm_caller_func"):
            self.llm_caller_func = call_llm_json
        self._initialized = True

    @parallel_batch(max_workers=5)
    def assign(
        self, 
        sentence: str,
        event: ExtractedEvent,
        entities: List[ExtractedEntity]
    ) -> Optional[AssignedEvent]:
        try:
            user_prompt = build_arguments_user_prompt(
                sentence, event, entities
            )
            raw_answer, result = self.llm_caller_func(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0
            )

            arguments = []
            for item in result.get('arguments', []):
                try:
                    arguments.append(Argument.model_validate(item))
                except Exception:
                    pass

            logger.info(f"Raw Answer: {raw_answer}")
            logger.info(f"Arguments: {arguments}")
            
            return AssignedEvent(
                type=event.type,
                trigger=event.trigger,
                arguments=arguments
            )
        except Exception as e:
            logger.error(e)
            return None

if __name__ == '__main__':
    from apps.extractors.entity_extractor import EntityExtractor
    from apps.extractors.event_extractor import EventExtractor
    
    entity_extractor = EntityExtractor()
    event_extractor = EventExtractor()
    assigner = ArgumentAssigner()

    sentence = "Ông chủ Nhà Trắng hồi tháng 8/2017 ân xá cho Joe Arpaio , cảnh sát trưởng hạt Maricopa , bang Arizona , bị buộc tội không tuân lệnh toà án trong một vụ án hình sự liên quan đến những người tình nghi là dân nhập cư bất hợp pháp ."
    
    entities = entity_extractor.extract(sentence)
    events = event_extractor.extract(sentence)

    logger.info(entities)
    logger.info(events)

    event = events[0]
    arguments = assigner.assign(sentence, event, entities)
    
    logger.info(arguments)