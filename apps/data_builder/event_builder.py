from apps.helpers.llm_caller import call_llm_json
from apps.helpers.prompt_builder import build_events_builder_system_prompt
from apps.models import MentionedEvent, EventReasoningItem, ExtractedEvent
from apps.helpers.decorators import parallel_batch, retry
from pydantic import BaseModel
from typing import List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventBuilder:
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

        self.system_prompt = build_events_builder_system_prompt()
        if not hasattr(self, "llm_caller_func"):
            self.llm_caller_func = call_llm_json
        self._initialized = True


    @parallel_batch(max_workers=5)
    @retry(max_attempts=3)
    def build(self, sentence: str, events: List[MentionedEvent]) -> EventReasoningItem:
        class SynthesizedEventResult(BaseModel):
            events: List[ExtractedEvent]

        try:
            gold_events_list = [{"trigger": ev.trigger, "type": ev.type.value if hasattr(ev.type, 'value') else ev.type} for ev in events]
            gold_events_json = json.dumps(gold_events_list, ensure_ascii=False)

            
            user_prompt = f'- Văn bản: "{sentence}"\n- Danh sách trigger mục tiêu: {gold_events_json}'

            raw_answer, result = self.llm_caller_func(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0
            )

            # Validate the JSON structure using Pydantic
            validated = SynthesizedEventResult.model_validate(result)

            # Compare with gold data
            gold_set = {(ev.trigger.strip(), ev.type.value if hasattr(ev.type, 'value') else str(ev.type)) for ev in events}
            pred_set = {(ev.trigger.strip(), ev.type.value if hasattr(ev.type, 'value') else str(ev.type)) for ev in validated.events}
            
            if gold_set and gold_set != pred_set:
                raise ValueError(
                    f"LLM generated event triggers do not match gold triggers.\n"
                    f"Gold: {gold_set}\nPred: {pred_set}"
                )



            logger.info(f"Generated reasoning for sentence: {sentence[:30]}...")
            return EventReasoningItem(
                sentence=sentence,
                events=events,
                reasoning=raw_answer
            )

        except Exception as e:
            logger.error(f"Error building event reasoning: {e}")
            return EventReasoningItem(
                sentence=sentence,
                events=events,
                reasoning=f"[LỖI] Không thể tạo suy luận: {str(e)}"
            )


if __name__ == '__main__':
    from apps.helpers.dataset_loader import load_base_dataset
    
    print("Loading test split of dataset...")
    dataset = load_base_dataset("test")
    
    builder = EventBuilder()
    
    # Process first sample as a test
    test_samples = dataset.items[:1]
    
    print(f"Generating reasoning for {len(test_samples)} samples...")
    for idx, sample in enumerate(test_samples):
        print(f"\n--- Sample {idx + 1} ---")
        print(f"Sentence: {sample.sentence}")
        print(f"Gold Events: {sample.events}")
        reasoning_item = builder.build(sample.sentence, sample.events)
        print(f"Generated Reasoning:\n{reasoning_item.reasoning}")
