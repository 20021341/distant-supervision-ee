from typing import Literal, Union, Tuple, Optional
import json
import re
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
from apps.constants import (
    FINETUNED_ENTITIES_SYSTEM_PROMPT,
    FINETUNED_EVENTS_SYSTEM_PROMPT,
    FINETUNED_ARGUMENTS_SYSTEM_PROMPT,
    FINETUNED_FULL_SYSTEM_PROMPT,
    SHORT_ENTITIES_SYSTEM_PROMPT,
    SHORT_EVENTS_SYSTEM_PROMPT,
    SHORT_ARGUMENTS_SYSTEM_PROMPT,
    SHORT_FULL_SYSTEM_PROMPT,
    SHORT_SYSTEM_PROMPTS
)


def split_cot_and_answer(text: str) -> Tuple[str, str]:
    """
    Splits reasoning text into (chain_of_thought, final_answer).
    Handles both markdown code blocks (```json ... ```) and raw JSON at the end.
    """
    text_stripped = text.strip()

    # If the text already contains <think>...</think>, extract what's inside and outside
    if "<think>" in text_stripped and "</think>" in text_stripped:
        parts = text_stripped.split("</think>", 1)
        cot = parts[0].replace("<think>", "").strip()
        ans = parts[1].strip()
        return cot, ans

    # Case 1: Markdown code block at the end: ```json ... ```
    m_code = list(re.finditer(r'```(?:json)?\s*(\{.*?\})\s*```', text_stripped, re.DOTALL))
    if m_code:
        last_m = m_code[-1]
        cot = text_stripped[:last_m.start()].strip()
        ans = last_m.group(0).strip()
        return cot, ans

    # Case 2: Raw JSON at the end, from matching outermost '{' to the last '}'
    last_brace = text_stripped.rfind('}')
    if last_brace != -1:
        depth = 0
        open_brace = -1
        for i in range(last_brace, -1, -1):
            if text_stripped[i] == '}':
                depth += 1
            elif text_stripped[i] == '{':
                depth -= 1
                if depth == 0:
                    open_brace = i
                    break
        if open_brace != -1:
            cot = text_stripped[:open_brace].strip()
            ans = text_stripped[open_brace:last_brace + 1].strip()
            return cot, ans

    return text_stripped, ""


def format_assistant_content(reasoning: str, model_type: str = "instruction", target_json: Optional[str] = None) -> str:
    """
    Formats the assistant target text based on model_type:
    - 'instruction': keeps the reasoning text as-is (standard output format with CoT).
    - 'reasoning': wraps the chain of thought within <think>...</think> tags,
      followed by the final answer/JSON outside.
    - 'json' / 'direct' / 'no_reasoning': outputs ONLY the JSON text, without reasoning.
    """
    if model_type in ("json", "direct", "no_reasoning", "direct_json"):
        if target_json:
            return target_json
        _, ans = split_cot_and_answer(reasoning)
        return ans or reasoning

    if model_type == "instruction":
        return reasoning

    if model_type == "reasoning":
        if "<think>" in reasoning and "</think>" in reasoning:
            return reasoning
        cot, ans = split_cot_and_answer(reasoning)
        if ans:
            return f"<think>\n{cot}\n</think>\n\n{ans}"
        else:
            return f"<think>\n{reasoning}\n</think>"

    raise ValueError(f"Unknown model_type: '{model_type}'. Expected 'instruction', 'reasoning', or 'json'/'direct'/'no_reasoning'.")


def convert_to_train_dataset(
    dataset: Union[EntityReasoningDataset, EventReasoningDataset, ArgumentReasoningDataset, FullReasoningDataset], 
    phase: Literal["entity", "event", "argument", "full"],
    tokenizer,
    model_type: Literal["instruction", "reasoning", "json", "direct", "no_reasoning"] = "instruction",
    system_prompt: Optional[str] = None
) -> HFDataset:
    sentences = []
    target_jsons = []
    texts = []

    is_direct_json = model_type in ("json", "direct", "no_reasoning", "direct_json")

    # Determine system prompt
    if system_prompt is not None:
        sys_prompt = system_prompt
    elif is_direct_json:
        sys_prompt = SHORT_SYSTEM_PROMPTS[phase]
    else:
        if phase == "entity":
            sys_prompt = FINETUNED_ENTITIES_SYSTEM_PROMPT
        elif phase == "event":
            sys_prompt = FINETUNED_EVENTS_SYSTEM_PROMPT
        elif phase == "argument":
            sys_prompt = FINETUNED_ARGUMENTS_SYSTEM_PROMPT
        elif phase == "full":
            sys_prompt = FINETUNED_FULL_SYSTEM_PROMPT

    if phase == "entity":
        for item in dataset:
            sentence = item.sentence
            entities_list = [{"text": ent.text, "type": ent.type.value if hasattr(ent.type, 'value') else ent.type} for ent in item.entities]
            target_data = {"entities": entities_list}
            target_json = json.dumps(target_data, ensure_ascii=False)
            
            assistant_content = format_assistant_content(item.reasoning, model_type=model_type, target_json=target_json)
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": assistant_content}
            ]
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            
            sentences.append(sentence)
            target_jsons.append(target_json)
            texts.append(text)

    elif phase == "event":
        for item in dataset:
            sentence = item.sentence
            events_list = [{"trigger": ev.trigger, "type": ev.type.value if hasattr(ev.type, 'value') else ev.type} for ev in item.events]
            target_data = {"events": events_list}
            target_json = json.dumps(target_data, ensure_ascii=False)
            
            assistant_content = format_assistant_content(item.reasoning, model_type=model_type, target_json=target_json)
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": assistant_content}
            ]
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            
            sentences.append(sentence)
            target_jsons.append(target_json)
            texts.append(text)

    elif phase == "argument":
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
            user_prompt = build_arguments_user_prompt(
                sentence,
                event_input,
                candidate_entities,
                include_hints=False if is_direct_json else True,
                include_schema=False if is_direct_json else True,
            )
            
            arguments_list = [{"text": arg.text, "type": arg.type.value if hasattr(arg.type, 'value') else arg.type} for arg in item.arguments]
            target_data = {"arguments": arguments_list}
            target_json = json.dumps(target_data, ensure_ascii=False)
            
            assistant_content = format_assistant_content(item.reasoning, model_type=model_type, target_json=target_json)
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": assistant_content}
            ]
            text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)
            
            sentences.append(sentence)
            target_jsons.append(target_json)
            texts.append(text)

    elif phase == "full":
        for item in dataset:
            sentence = item.sentence
            entities_list = [{"text": ent.text, "type": ent.type.value if hasattr(ent.type, 'value') else ent.type} for ent in item.entities]
            events_list = []
            for ev in item.events:
                args_list = [{"text": arg.text, "type": arg.type.value if hasattr(arg.type, 'value') else arg.type} for arg in ev.arguments]
                events_list.append({
                    "type": ev.type.value if hasattr(ev.type, 'value') else ev.type,
                    "trigger": ev.trigger,
                    "arguments": args_list
                })
            
            target_data = {
                "entities": entities_list,
                "events": events_list
            }
            target_json = json.dumps(target_data, ensure_ascii=False)
            
            assistant_content = format_assistant_content(item.reasoning, model_type=model_type, target_json=target_json)
            messages = [
                {"role": "system", "content": sys_prompt},
                {"role": "user", "content": sentence},
                {"role": "assistant", "content": assistant_content}
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

        print("\n=== Test conversion for phase 'entity' (instruction) ===")
        hf_dataset = convert_to_train_dataset(dataset, "entity", tokenizer, model_type="instruction")
        print(f"Total samples converted: {len(hf_dataset)}")
        if len(hf_dataset) > 0:
            print(f"Text (Instruction):\n{hf_dataset[0]['text']}")

        print("\n=== Test conversion for phase 'entity' (reasoning) ===")
        hf_reasoning = convert_to_train_dataset(dataset, "entity", tokenizer, model_type="reasoning")
        if len(hf_reasoning) > 0:
            print(f"Text (Reasoning with <think>):\n{hf_reasoning[0]['text']}")

        print("\n=== Test conversion for phase 'entity' (json/direct - short prompt, no reasoning) ===")
        hf_json = convert_to_train_dataset(dataset, "entity", tokenizer, model_type="json")
        if len(hf_json) > 0:
            print(f"Text (JSON Direct):\n{hf_json[0]['text']}")
    except Exception as e:
        print(f"Could not load or convert: {e}")


