from apps.constants import *
from apps.models import ExtractedEvent, ExtractedEntity, Argument
from typing import List
from itertools import chain
import json



def build_entities_system_prompt(include_hints: bool = True, few_shot: bool = False):
    entity_types_text = ""
    for index, entity_type in enumerate(ENTITY_TYPES, start=1):
        entity_types_text += f"{index}. {entity_type}\n"
        if include_hints:
            entity_types_text += f"{ENTITY_TYPES[entity_type]}\n\n---\n\n"

    prompt = ENTITIES_SYSTEM_PROMPT_TEMPLATE.format(
        entity_types_text=entity_types_text
    )

    if few_shot:
        prompt += "\n\n## VÍ DỤ MẪU THAM KHẢO:\n" + ENTITIES_FEW_SHOT_EXAMPLES

    return prompt

def build_events_system_prompt(include_hints: bool = True, few_shot: bool = False):
    event_types_text = ""
    for index, event_type in enumerate(EVENT_TYPES, start=1):
        event_types_text += f"{index}. {event_type}\n"
        if include_hints:
            event_types_text += f"{EVENT_TYPES[event_type]}\n\n---\n\n"

    prompt = EVENTS_SYSTEM_PROMPT_TEMPLATE.format(
        event_types_text=event_types_text
    )

    if few_shot:
        prompt += "\n\n## VÍ DỤ MẪU THAM KHẢO:\n" + EVENTS_FEW_SHOT_EXAMPLES

    return prompt

def build_arguments_system_prompt(few_shot: bool = False):
    prompt = EVENT_ARGUMENTS_SYSTEM_PROMPT_TEMPLATE

    if few_shot:
        prompt += "\n\n## VÍ DỤ MẪU THAM KHẢO:\n" + EVENT_ARGUMENTS_FEW_SHOT_EXAMPLES

    return prompt

def build_arguments_user_prompt(
    sentence: str,
    event: ExtractedEvent,
    entities: List[ExtractedEntity],
    include_hints: bool = True
) -> str:
    event_type, event_trigger = event.type, event.trigger
    event_schema = EVENT_ARGUMENTS_SCHEMA.get(event_type.value, None)
    assert event_schema, f"Missing argument schema for {event_type}"

    valid_argument_types = event_schema['schema'].keys()
    valid_arguments_hint = ""
    for index, argument_type in enumerate(valid_argument_types, start=1):
        valid_arguments_hint += f"{index}. {argument_type}\n"
        if include_hints:
            valid_arguments_hint += f"{ARGUMENT_TYPES[argument_type]}\n\n---\n\n"

    valid_entity_types = list(set(chain(*[event_schema['schema'][arg_type] for arg_type in event_schema['schema']])))
    valid_entities = [entity for entity in entities if entity.type.value in valid_entity_types]


    return """
- Văn bản: "{sentence}"
- Loại sự kiện: "{event_type}"
- Trigger sự kiện: "{event_trigger}"
- Danh sách thực thể ứng viên: "{entities}"
- Danh sách loại tham số sự kiện:
{arguments_hint}
""".format(
        sentence=sentence,
        event_type=event_type.value,
        event_trigger=event_trigger,
        entities=json.dumps([entity.model_dump(mode='json') for entity in valid_entities], ensure_ascii=False),
        arguments_hint=valid_arguments_hint
    )

def build_full_system_prompt(include_hints: bool = True, few_shot: bool = False):
    entity_types_text = ""
    for index, entity_type in enumerate(ENTITY_TYPES, start=1):
        entity_types_text += f"{index}. {entity_type}\n"
        if include_hints:
            entity_types_text += f"{ENTITY_TYPES[entity_type]}\n\n---\n\n"

    event_types_text = ""
    for index, event_type in enumerate(EVENT_TYPES, start=1):
        event_types_text += f"{index}. {event_type}\n"
        if include_hints:
            event_types_text += f"{EVENT_TYPES[event_type]}\n\n---\n\n"

    argument_types_text = ""
    for index, argument_type in enumerate(ARGUMENT_TYPES, start=1):
        argument_types_text += f"{index}. {argument_type}\n"
        if include_hints:
            argument_types_text += f"{ARGUMENT_TYPES[argument_type]}\n\n---\n\n"

    prompt = FULL_SYSTEM_PROMPT_TEMPLATE.format(
        entity_types_text=entity_types_text,
        event_types_text=event_types_text,
        argument_types_text=argument_types_text
    )

    if few_shot:
        prompt += "\n\n## VÍ DỤ MẪU THAM KHẢO:\n" + FULL_FEW_SHOT_EXAMPLES

    return prompt

def build_entities_builder_system_prompt(include_hints: bool = True, few_shot: bool = True):
    entity_types_text = ""
    for index, entity_type in enumerate(ENTITY_TYPES, start=1):
        entity_types_text += f"{index}. {entity_type}\n"
        if include_hints:
            entity_types_text += f"{ENTITY_TYPES[entity_type]}\n\n---\n\n"

    prompt = ENTITIES_BUILDER_SYSTEM_PROMPT_TEMPLATE.format(
        entity_types_text=entity_types_text
    )

    if few_shot:
        prompt += "\n\n## VÍ DỤ MẪU THAM KHẢO:\n" + ENTITIES_FEW_SHOT_EXAMPLES

    return prompt

def build_events_builder_system_prompt(include_hints: bool = True, few_shot: bool = True):
    event_types_text = ""
    for index, event_type in enumerate(EVENT_TYPES, start=1):
        event_types_text += f"{index}. {event_type}\n"
        if include_hints:
            event_types_text += f"{EVENT_TYPES[event_type]}\n\n---\n\n"

    prompt = EVENTS_BUILDER_SYSTEM_PROMPT_TEMPLATE.format(
        event_types_text=event_types_text
    )

    if few_shot:
        prompt += "\n\n## VÍ DỤ MẪU THAM KHẢO:\n" + EVENTS_FEW_SHOT_EXAMPLES

    return prompt

def build_arguments_builder_system_prompt(few_shot: bool = True):
    prompt = EVENT_ARGUMENTS_BUILDER_SYSTEM_PROMPT_TEMPLATE

    if few_shot:
        prompt += "\n\n## VÍ DỤ MẪU THAM KHẢO:\n" + EVENT_ARGUMENTS_FEW_SHOT_EXAMPLES

    return prompt

def build_arguments_builder_user_prompt(
    sentence: str,
    event: ExtractedEvent,
    entities: List[ExtractedEntity],
    gold_arguments: List[Argument],
    include_hints: bool = True
) -> str:
    base_user_prompt = build_arguments_user_prompt(
        sentence=sentence,
        event=event,
        entities=entities,
        include_hints=include_hints
    )
    gold_args_list = [{"text": arg.text, "type": arg.type.value if hasattr(arg.type, 'value') else arg.type} for arg in gold_arguments]
    gold_args_json = json.dumps(gold_args_list, ensure_ascii=False)

    return base_user_prompt + f"- Danh sách đối số mục tiêu: {gold_args_json}\n"

def build_full_builder_system_prompt(include_hints: bool = True, few_shot: bool = True):
    entity_types_text = ""
    for index, entity_type in enumerate(ENTITY_TYPES, start=1):
        entity_types_text += f"{index}. {entity_type}\n"
        if include_hints:
            entity_types_text += f"{ENTITY_TYPES[entity_type]}\n\n---\n\n"

    event_types_text = ""
    for index, event_type in enumerate(EVENT_TYPES, start=1):
        event_types_text += f"{index}. {event_type}\n"
        if include_hints:
            event_types_text += f"{EVENT_TYPES[event_type]}\n\n---\n\n"

    argument_types_text = ""
    for index, argument_type in enumerate(ARGUMENT_TYPES, start=1):
        argument_types_text += f"{index}. {argument_type}\n"
        if include_hints:
            argument_types_text += f"{ARGUMENT_TYPES[argument_type]}\n\n---\n\n"

    prompt = FULL_BUILDER_SYSTEM_PROMPT_TEMPLATE.format(
        entity_types_text=entity_types_text,
        event_types_text=event_types_text,
        argument_types_text=argument_types_text
    )

    if few_shot:
        prompt += "\n\n## VÍ DỤ MẪU THAM KHẢO:\n" + FULL_FEW_SHOT_EXAMPLES

    return prompt
