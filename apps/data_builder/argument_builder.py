from apps.helpers.llm_caller import call_llm_json
from apps.helpers.prompt_builder import (
    build_arguments_builder_system_prompt,
    build_arguments_builder_user_prompt
)
from apps.models import MentionedEntity, Argument, ArgumentReasoningItem, ExtractedEvent, ExtractedEntity, EventType
from apps.helpers.decorators import parallel_batch, retry
from pydantic import BaseModel
from typing import List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ArgumentBuilder:
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

        self.system_prompt = build_arguments_builder_system_prompt()
        if not hasattr(self, "llm_caller_func"):
            self.llm_caller_func = call_llm_json
        self._initialized = True


    @parallel_batch(max_workers=5)
    @retry(max_attempts=3)
    def build(
        self,
        sentence: str,
        event_type: str,
        event_trigger: str,
        entities: List[MentionedEntity],
        gold_arguments: List[Argument]
    ) -> ArgumentReasoningItem:
        class SynthesizedArgumentResult(BaseModel):
            arguments: List[Argument]

        try:
            if isinstance(event_type, str):
                ev_type_enum = EventType(event_type)
            else:
                ev_type_enum = event_type
                
            event_obj = ExtractedEvent(type=ev_type_enum, trigger=event_trigger)
            candidate_entities = [
                ExtractedEntity(text=ent.text, type=ent.type)
                for ent in entities
            ]
            
            user_prompt = build_arguments_builder_user_prompt(
                sentence=sentence,
                event=event_obj,
                entities=candidate_entities,
                gold_arguments=gold_arguments
            )
            
            raw_answer, result = self.llm_caller_func(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0
            )

            # Validate the JSON structure using Pydantic
            validated = SynthesizedArgumentResult.model_validate(result)

            # Compare with gold data
            gold_set = {(arg.text.strip(), arg.type.value if hasattr(arg.type, 'value') else str(arg.type)) for arg in gold_arguments}
            pred_set = {(arg.text.strip(), arg.type.value if hasattr(arg.type, 'value') else str(arg.type)) for arg in validated.arguments}
            
            if gold_set and gold_set != pred_set:
                raise ValueError(
                    f"LLM generated arguments do not match gold arguments.\n"
                    f"Gold: {gold_set}\nPred: {pred_set}"
                )



            logger.info(f"Generated reasoning for sentence: {sentence[:30]}...")
            return ArgumentReasoningItem(
                sentence=sentence,
                event_type=ev_type_enum,
                event_trigger=event_trigger,
                entities=entities,
                arguments=gold_arguments,
                reasoning=raw_answer
            )


        except Exception as e:
            logger.error(f"Error building argument reasoning: {e}")
            ev_type_enum = event_type if not isinstance(event_type, str) else EventType(event_type)
            return ArgumentReasoningItem(
                sentence=sentence,
                event_type=ev_type_enum,
                event_trigger=event_trigger,
                entities=entities,
                arguments=gold_arguments,
                reasoning=f"[LỖI] Không thể tạo suy luận: {str(e)}"
            )

if __name__ == '__main__':
    from apps.helpers.dataset_loader import load_base_dataset
    
    print("Loading test split of dataset...")
    dataset = load_base_dataset("test")
    
    builder = ArgumentBuilder()
    
    # Find first sample with an event and arguments
    test_sample = None
    for sample in dataset.items:
        if sample.events and sample.events[0].arguments:
            test_sample = sample
            break
            
    if test_sample:
        print(f"Sentence: {test_sample.sentence}")
        event = test_sample.events[0]
        print(f"Event: type={event.type}, trigger={event.trigger}")
        print(f"Entities: {test_sample.entities}")
        print(f"Gold Arguments: {event.arguments}")
        
        reasoning_item = builder.build(
            sentence=test_sample.sentence,
            event_type=event.type,
            event_trigger=event.trigger,
            entities=test_sample.entities,
            gold_arguments=event.arguments
        )
        print(f"\nGenerated Reasoning:\n{reasoning_item.reasoning}")
    else:
        print("No samples with events and arguments found.")
