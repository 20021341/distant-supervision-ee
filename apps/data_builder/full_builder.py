from apps.helpers.llm_caller import call_llm_json
from apps.helpers.prompt_builder import build_full_builder_system_prompt
from apps.models import MentionedEntity, MentionedEvent, FullReasoningItem
from apps.helpers.decorators import parallel_batch, retry
from pydantic import BaseModel
from typing import List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FullBuilder:
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

        self.system_prompt = build_full_builder_system_prompt()
        if not hasattr(self, "llm_caller_func"):
            self.llm_caller_func = call_llm_json
        self._initialized = True


    @parallel_batch(max_workers=5)
    @retry(max_attempts=3)
    def build(self, sentence: str, entities: List[MentionedEntity], events: List[MentionedEvent]) -> FullReasoningItem:
        class SynthesizedFullResult(BaseModel):
            entities: List[MentionedEntity]
            events: List[MentionedEvent]

        try:
            gold_entities_list = [{"text": ent.text, "type": ent.type.value if hasattr(ent.type, 'value') else ent.type} for ent in entities]
            
            gold_events_list = []
            for ev in events:
                args_list = [{"text": arg.text, "type": arg.type.value if hasattr(arg.type, 'value') else arg.type} for arg in ev.arguments]
                gold_events_list.append({
                    "type": ev.type.value if hasattr(ev.type, 'value') else ev.type,
                    "trigger": ev.trigger,
                    "arguments": args_list
                })
                
            gold_data = {
                "entities": gold_entities_list,
                "events": gold_events_list
            }
            gold_json = json.dumps(gold_data, ensure_ascii=False)
            
            user_prompt = f'- Văn bản: "{sentence}"\n- Danh sách mục tiêu: {gold_json}'
            
            # Add strict instruction if gold entities or events are empty
            if not entities or not events:
                user_prompt += (
                    "\nLưu ý đặc biệt: Danh sách mục tiêu được cung cấp là chân lý tuyệt đối. "
                    "Vì danh sách thực thể hoặc sự kiện mục tiêu ở trên có phần rỗng (danh sách []), bạn BẮT BUỘC "
                    "phải viết suy luận giải thích tại sao câu văn này không chứa thực thể hoặc sự kiện nào tương ứng, "
                    "và đầu ra JSON bắt buộc phải trả về danh sách rỗng giống như mục tiêu."
                )


            raw_answer, result = self.llm_caller_func(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0
            )

            # Validate the JSON structure using Pydantic
            validated = SynthesizedFullResult.model_validate(result)

            # Compare entities
            gold_ent_set = {(ent.text.strip(), ent.type.value if hasattr(ent.type, 'value') else str(ent.type)) for ent in entities}
            pred_ent_set = {(ent.text.strip(), ent.type.value if hasattr(ent.type, 'value') else str(ent.type)) for ent in validated.entities}
            
            if gold_ent_set != pred_ent_set:
                raise ValueError(
                    f"LLM generated entities do not match gold entities.\n"
                    f"Gold: {gold_ent_set}\nPred: {pred_ent_set}"
                )

            # Compare events and their nested arguments
            def get_events_set(ev_list):
                res = set()
                for ev in ev_list:
                    ev_type = ev.type.value if hasattr(ev.type, 'value') else str(ev.type)
                    args = frozenset(
                        (arg.text.strip(), arg.type.value if hasattr(arg.type, 'value') else str(arg.type))
                        for arg in ev.arguments
                    )
                    res.add((ev.trigger.strip(), ev_type, args))
                return res

            gold_evt_set = get_events_set(events)
            pred_evt_set = get_events_set(validated.events)
            
            if gold_evt_set != pred_evt_set:
                raise ValueError(
                    f"LLM generated events do not match gold events.\n"
                    f"Gold: {gold_evt_set}\nPred: {pred_evt_set}"
                )


            logger.info(f"Generated reasoning for sentence: {sentence[:30]}...")
            return FullReasoningItem(
                sentence=sentence,
                entities=entities,
                events=events,
                reasoning=raw_answer
            )

        except Exception as e:
            logger.error(f"Error building full reasoning: {e}")
            return FullReasoningItem(
                sentence=sentence,
                entities=entities,
                events=events,
                reasoning=f"[LỖI] Không thể tạo suy luận: {str(e)}"
            )


if __name__ == '__main__':
    from apps.helpers.dataset_loader import load_base_dataset
    
    print("Loading test split of dataset...")
    dataset = load_base_dataset("test")
    
    builder = FullBuilder()
    
    # Process first sample as a test
    test_samples = dataset.items[:1]
    
    print(f"Generating reasoning for {len(test_samples)} samples...")
    for idx, sample in enumerate(test_samples):
        print(f"\n--- Sample {idx + 1} ---")
        print(f"Sentence: {sample.sentence}")
        print(f"Entities: {sample.entities}")
        print(f"Events: {sample.events}")
        reasoning_item = builder.build(sample.sentence, sample.entities, sample.events)
        print(f"Generated Reasoning:\n{reasoning_item.reasoning}")
