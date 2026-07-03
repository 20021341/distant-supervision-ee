from apps.helpers.llm_caller import call_llm_json
from apps.helpers.prompt_builder import build_entities_builder_system_prompt
from apps.models import MentionedEntity, EntityReasoningItem
from apps.helpers.decorators import parallel_batch, retry
from pydantic import BaseModel
from typing import List
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EntityBuilder:
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

        self.system_prompt = build_entities_builder_system_prompt()
        if not hasattr(self, "llm_caller_func"):
            self.llm_caller_func = call_llm_json
        self._initialized = True


    @parallel_batch(max_workers=5)
    @retry(max_attempts=3)
    def build(self, sentence: str, entities: List[MentionedEntity]) -> EntityReasoningItem:
        class SynthesizedEntityResult(BaseModel):
            entities: List[MentionedEntity]

        try:
            gold_entities_list = [{"text": ent.text, "type": ent.type.value if hasattr(ent.type, 'value') else ent.type} for ent in entities]
            gold_entities_json = json.dumps(gold_entities_list, ensure_ascii=False)

            
            user_prompt = f'- Văn bản: "{sentence}"\n- Danh sách thực thể mục tiêu: {gold_entities_json}'

            raw_answer, result = self.llm_caller_func(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt,
                temperature=0
            )

            # Validate the JSON structure using Pydantic
            validated = SynthesizedEntityResult.model_validate(result)

            # Compare with gold data
            gold_set = {(ent.text.strip(), ent.type.value if hasattr(ent.type, 'value') else str(ent.type)) for ent in entities}
            pred_set = {(ent.text.strip(), ent.type.value if hasattr(ent.type, 'value') else str(ent.type)) for ent in validated.entities}
            
            if gold_set and gold_set != pred_set:
                raise ValueError(
                    f"LLM generated entities do not match gold entities.\n"
                    f"Gold: {gold_set}\nPred: {pred_set}"
                )



            logger.info(f"Generated reasoning for sentence: {sentence[:30]}...")
            return EntityReasoningItem(
                sentence=sentence,
                entities=entities,
                reasoning=raw_answer
            )

        except Exception as e:
            logger.error(f"Error building entity reasoning: {e}")
            return EntityReasoningItem(
                sentence=sentence,
                entities=entities,
                reasoning=f"[LỖI] Không thể tạo suy luận: {str(e)}"
            )


if __name__ == '__main__':
    from apps.helpers.dataset_loader import load_base_dataset
    from apps.models import EntityReasoningDataset
    
    print("Loading test split of dataset...")
    dataset = load_base_dataset("test")
    
    builder = EntityBuilder()
    
    # Process first sample as a test
    test_samples = dataset.items[:1]
    
    print(f"Generating reasoning for {len(test_samples)} samples...")
    reasoning_items = []
    for idx, sample in enumerate(test_samples):
        print(f"\n--- Sample {idx + 1} ---")
        print(f"Sentence: {sample.sentence}")
        print(f"Gold Entities: {sample.entities}")
        reasoning_item = builder.build(sample.sentence, sample.entities)
        reasoning_items.append(reasoning_item)
        print(f"Generated Reasoning:\n{reasoning_item.reasoning}")
        
    reasoning_dataset = EntityReasoningDataset(items=reasoning_items)
    print("Saving entity reasoning dataset to dataset directory...")
    reasoning_dataset.save("test")
    print("Dataset saved successfully!")

