from apps.models import (
    Dataset, DatasetItem, MentionedEntity, MentionedEvent, Argument,
    EntityReasoningDataset, EntityReasoningItem,
    EventReasoningDataset, EventReasoningItem,
    ArgumentReasoningDataset, ArgumentReasoningItem,
    FullReasoningDataset, FullReasoningItem
)
from typing import List, Literal
import json
import os

DATASET_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'dataset')

def load_base_dataset(split: Literal["train", "test"]) -> Dataset:
    file_path = os.path.join(DATASET_DIR, f"{split}.jsonl")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = [json.loads(line) for line in f.readlines() if line]

    dataset_items = []

    for d in data:
        entities = [
            MentionedEntity(
                type=entity['entity_type'],
                text=entity['text']
            ) for entity in d['entity_mentions']
        ]

        events = [
            MentionedEvent(
                type=event['event_type'],
                trigger=event['trigger']['text'],
                arguments=[
                    Argument(
                        type=arg['role'],
                        text=arg['text']
                    ) for arg in event['arguments']
                ]
            ) for event in d['event_mentions']
        ]

        dataset_items.append(DatasetItem(
            sentence=d['sentence'],
            entities=entities,
            events=events
        ))


    return Dataset(items=dataset_items)

def _load_jsonl_robust(file_path: str) -> list:
    data = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return data

def load_entity_reasoning_dataset(split: Literal["train", "test"]) -> EntityReasoningDataset:
    file_path = os.path.join(DATASET_DIR, f"{split}_entity_reasoning.jsonl")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    data = _load_jsonl_robust(file_path)
        
    items = []
    for d in data:
        entities = [
            MentionedEntity(
                type=ent["type"],
                text=ent["text"]
            ) for ent in d["entity_mentions"]
        ]
        items.append(EntityReasoningItem(
            sentence=d["sentence"],
            entities=entities,
            reasoning=d["reasoning"]
        ))
    return EntityReasoningDataset(items=items)

def load_event_reasoning_dataset(split: Literal["train", "test"]) -> EventReasoningDataset:
    file_path = os.path.join(DATASET_DIR, f"{split}_event_reasoning.jsonl")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    data = _load_jsonl_robust(file_path)
        
    items = []
    for d in data:
        events = [
            MentionedEvent(
                type=ev["type"],
                trigger=ev["trigger"]["text"],
                arguments=[
                    Argument(
                        type=arg["type"],
                        text=arg["text"]
                    ) for arg in ev["arguments"]
                ]
            ) for ev in d["event_mentions"]
        ]
        items.append(EventReasoningItem(
            sentence=d["sentence"],
            events=events,
            reasoning=d["reasoning"]
        ))
    return EventReasoningDataset(items=items)

def load_argument_reasoning_dataset(split: Literal["train", "test"]) -> ArgumentReasoningDataset:
    file_path = os.path.join(DATASET_DIR, f"{split}_argument_reasoning.jsonl")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    data = _load_jsonl_robust(file_path)
        
    items = []
    for d in data:
        entities = [
            MentionedEntity(
                type=ent["type"],
                text=ent["text"]
            ) for ent in d["entity_mentions"]
        ]
        arguments = [
            Argument(
                type=arg["type"],
                text=arg["text"]
            ) for arg in d["arguments"]
        ]
        items.append(ArgumentReasoningItem(
            sentence=d["sentence"],
            event_type=d["type"],
            event_trigger=d["trigger"],
            entities=entities,
            arguments=arguments,
            reasoning=d["reasoning"]
        ))
    return ArgumentReasoningDataset(items=items)

def load_full_reasoning_dataset(split: Literal["train", "test"]) -> FullReasoningDataset:
    file_path = os.path.join(DATASET_DIR, f"{split}_full_reasoning.jsonl")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    data = _load_jsonl_robust(file_path)
        
    items = []
    for d in data:
        entities = [
            MentionedEntity(
                type=ent["type"],
                text=ent["text"]
            ) for ent in d["entity_mentions"]
        ]
        events = [
            MentionedEvent(
                type=ev["type"],
                trigger=ev["trigger"]["text"],
                arguments=[
                    Argument(
                        type=arg["type"],
                        text=arg["text"]
                    ) for arg in ev["arguments"]
                ]
            ) for ev in d["event_mentions"]
        ]
        items.append(FullReasoningItem(
            sentence=d["sentence"],
            entities=entities,
            events=events,
            reasoning=d["reasoning"]
        ))
    return FullReasoningDataset(items=items)



if __name__ == '__main__':
    dataset = load_base_dataset("test")

    for item in dataset.items[:1]:
        print(item.sentence)
        print(item.entities)
        print(item.events)

    try:
        reasoning_dataset = load_entity_reasoning_dataset("test")
        print(f"\nSuccessfully loaded entity reasoning dataset with {len(reasoning_dataset)} samples.")
        print(f"First sample reasoning:\n{reasoning_dataset[0].reasoning[:100]}...")
    except Exception as e:
        print(f"\nCould not load reasoning dataset: {e}")

