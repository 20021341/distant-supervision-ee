from typing import Literal, Union
import json
from datasets import Dataset as HFDataset
from apps.models import (
    EntityReasoningDataset,
    EventReasoningDataset,
    ArgumentReasoningDataset,
    FullReasoningDataset,
    ExtractedEntity,
    ExtractedEvent
)
from apps.helpers.prompt_builder import (
    build_entities_system_prompt,
    build_events_system_prompt,
    build_arguments_system_prompt,
    build_arguments_user_prompt,
    build_full_system_prompt
)

def convert_to_train_dataset(
    dataset: Union[EntityReasoningDataset, EventReasoningDataset, ArgumentReasoningDataset, FullReasoningDataset], 
    phase: Literal["entity", "event", "argument", "full"],
    tokenizer
) -> HFDataset:
    sentences = []
    target_jsons = []
    texts = []

    if phase == "entity":
        sys_prompt = build_entities_system_prompt()
        for item in dataset:
            sentence = item.sentence
            entities_list = [{"text": ent.text, "type": ent.type.value if hasattr(ent.type, 'value') else ent.type} for ent in item.entities]
            target_data = {"entities": entities_list}
            target_json = json.dumps(target_data, separators=(',', ':'), ensure_ascii=False)
            
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": item.reasoning}
            ]
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            
            sentences.append(sentence)
            target_jsons.append(target_json)
            texts.append(text)

    elif phase == "event":
        sys_prompt = build_events_system_prompt()
        for item in dataset:
            sentence = item.sentence
            events_list = [{"trigger": ev.trigger, "type": ev.type.value if hasattr(ev.type, 'value') else ev.type} for ev in item.events]
            target_data = {"events": events_list}
            target_json = json.dumps(target_data, separators=(',', ':'), ensure_ascii=False)
            
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": item.reasoning}
            ]
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            
            sentences.append(sentence)
            target_jsons.append(target_json)
            texts.append(text)

    elif phase == "argument":
        sys_prompt = build_arguments_system_prompt()
        for item in dataset:
            sentence = item.sentence
            event_input = ExtractedEvent(
                type=item.event_type,
                trigger=item.event_trigger
            )
            candidate_entities = [
                ExtractedEntity(text=ent.text, type=ent.type)
                for ent in item.entities
            ]
            user_prompt = build_arguments_user_prompt(sentence, event_input, candidate_entities)
            
            arguments_list = [{"text": arg.text, "type": arg.type.value if hasattr(arg.type, 'value') else arg.type} for arg in item.arguments]
            target_data = {"arguments": arguments_list}
            target_json = json.dumps(target_data, separators=(',', ':'), ensure_ascii=False)
            
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": item.reasoning}
            ]
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            
            sentences.append(sentence)
            target_jsons.append(target_json)
            texts.append(text)

    elif phase == "full":
        sys_prompt = build_full_system_prompt()
        for item in dataset:
            sentence = item.sentence
            entities_list = [{"type": ent.type.value if hasattr(ent.type, 'value') else ent.type, "text": ent.text} for ent in item.entities]
            events_list = []
            for ev in item.events:
                args_list = [{"type": arg.type.value if hasattr(arg.type, 'value') else arg.type, "text": arg.text} for arg in ev.arguments]
                events_list.append({
                    "type": ev.type.value if hasattr(ev.type, 'value') else ev.type,
                    "trigger": ev.trigger,
                    "arguments": args_list
                })
            
            target_data = {
                "entities": entities_list,
                "events": events_list
            }
            target_json = json.dumps(target_data, separators=(',', ':'), ensure_ascii=False)
            
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": item.reasoning}
            ]
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            
            sentences.append(sentence)
            target_jsons.append(target_json)
            texts.append(text)

    return HFDataset.from_dict({
        "sentence": sentences,
        "target_json": target_jsons,
        "text": texts
    })


if __name__ == "__main__":
    from apps.helpers.dataset_loader import load_entity_reasoning_dataset
    from transformers import AutoTokenizer

    print("Loading tokenizer for Qwen/Qwen2.5-7B-Instruct...")
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")

    try:
        print("Loading test entity reasoning dataset...")
        dataset = load_entity_reasoning_dataset("test")

        print("\n=== Test conversion for phase 'entity' ===")
        hf_dataset = convert_to_train_dataset(dataset, "entity", tokenizer)
        print(f"Total samples converted: {len(hf_dataset)}")
        
        if len(hf_dataset) > 0:
            print("\n--- First Sample Details ---")
            print(f"Sentence: {hf_dataset[0]['sentence']}")
            print(f"Target JSON: {hf_dataset[0]['target_json']}")
            print(f"Text (Formatted Chat Prompt):\n{hf_dataset[0]['text']}")
    except Exception as e:
        print(f"Could not load or convert: {e}")


