from pydantic import BaseModel, field_validator
from apps.constants import ENTITY_TYPES, EVENT_TYPES, ARGUMENT_TYPES
from enum import Enum
from typing import List, Iterator
import os
import json

DATASET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset"))


EntityType = Enum("EntityType", {k: k for k in ENTITY_TYPES}, type=str)
EventType = Enum("EventType", {k: k for k in EVENT_TYPES}, type=str)
ArgumentType = Enum("ArgumentType", {k: k for k in ARGUMENT_TYPES}, type=str)

# ====================
# GROUND TRUTH CLASSES
# ====================
class MentionedEntity(BaseModel):
    type: EntityType
    text: str

class Argument(BaseModel):
    model_config = {"extra": "forbid"}
    type: ArgumentType
    text: str

class MentionedEvent(BaseModel):
    type: EventType
    trigger: str
    arguments: List[Argument]
    
# ====================
# EXTRACTED CLASSES
# ====================
class ExtractedEntity(BaseModel):
    model_config = {"extra": "forbid"}
    text: str
    type: EntityType

class ExtractedEvent(BaseModel):
    model_config = {"extra": "forbid"}
    trigger: str
    type: EventType

class AssignedEvent(BaseModel):
    model_config = {"extra": "forbid"}
    type: EventType
    trigger: str
    arguments: List[Argument]

    @field_validator('arguments', mode='before')
    @classmethod
    def filter_arguments(cls, v):
        if not isinstance(v, list):
            return v
        filtered = []
        for arg in v:
            try:
                if isinstance(arg, dict):
                    Argument.model_validate(arg)
                    filtered.append(arg)
                elif isinstance(arg, Argument):
                    filtered.append(arg)
            except Exception:
                pass
        return filtered

class PredictedItem(BaseModel):
    model_config = {"extra": "forbid"}
    entities: List[ExtractedEntity]
    events: List[AssignedEvent]

    @field_validator('entities', mode='before')
    @classmethod
    def filter_entities(cls, v):
        if not isinstance(v, list):
            return v
        filtered = []
        for ent in v:
            try:
                if isinstance(ent, dict):
                    ExtractedEntity.model_validate(ent)
                    filtered.append(ent)
                elif isinstance(ent, ExtractedEntity):
                    filtered.append(ent)
            except Exception:
                pass
        return filtered

    @field_validator('events', mode='before')
    @classmethod
    def filter_events(cls, v):
        if not isinstance(v, list):
            return v
        filtered = []
        for ev in v:
            try:
                if isinstance(ev, dict):
                    AssignedEvent.model_validate(ev)
                    filtered.append(ev)
                elif isinstance(ev, AssignedEvent):
                    filtered.append(ev)
            except Exception:
                pass
        return filtered

class DatasetItem(BaseModel):
    sentence: str
    entities: List[MentionedEntity]
    events: List[MentionedEvent]

class Dataset(BaseModel):
    items: List[DatasetItem]

    def __iter__(self) -> Iterator[DatasetItem]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> DatasetItem:
        return self.items[index]


class EntityReasoningItem(BaseModel):
    sentence: str
    entities: List[MentionedEntity]
    reasoning: str


class EntityReasoningDataset(BaseModel):
    items: List[EntityReasoningItem]

    def __iter__(self) -> Iterator[EntityReasoningItem]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> EntityReasoningItem:
        return self.items[index]

    def save(self, split: str) -> None:
        file_path = os.path.join(DATASET_DIR, f"{split}_entity_reasoning.jsonl")
        os.makedirs(DATASET_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            for item in self.items:
                d = {
                    "sentence": item.sentence,
                    "entity_mentions": [
                        {
                            "text": ent.text,
                            "type": ent.type.value if hasattr(ent.type, 'value') else str(ent.type)
                        } for ent in item.entities
                    ],
                    "reasoning": item.reasoning
                }
                f.write(json.dumps(d, ensure_ascii=False) + "\n")

    @classmethod
    def save_item(cls, split: str, item: EntityReasoningItem) -> None:
        file_path = os.path.join(DATASET_DIR, f"{split}_entity_reasoning.jsonl")
        os.makedirs(DATASET_DIR, exist_ok=True)
        d = {
            "sentence": item.sentence,
            "entity_mentions": [
                {
                    "text": ent.text,
                    "type": ent.type.value if hasattr(ent.type, 'value') else str(ent.type)
                } for ent in item.entities
            ],
            "reasoning": item.reasoning
        }
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")





class EventReasoningItem(BaseModel):
    sentence: str
    events: List[MentionedEvent]
    reasoning: str


class EventReasoningDataset(BaseModel):
    items: List[EventReasoningItem]

    def __iter__(self) -> Iterator[EventReasoningItem]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> EventReasoningItem:
        return self.items[index]

    def save(self, split: str) -> None:
        file_path = os.path.join(DATASET_DIR, f"{split}_event_reasoning.jsonl")
        os.makedirs(DATASET_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            for item in self.items:
                d = {
                    "sentence": item.sentence,
                    "event_mentions": [
                        {
                            "type": ev.type.value if hasattr(ev.type, 'value') else str(ev.type),
                            "trigger": {"text": ev.trigger},
                            "arguments": [
                                {
                                    "type": arg.type.value if hasattr(arg.type, 'value') else str(arg.type),
                                    "text": arg.text
                                } for arg in ev.arguments
                            ]
                        } for ev in item.events
                    ],
                    "reasoning": item.reasoning
                }
                f.write(json.dumps(d, ensure_ascii=False) + "\n")

    @classmethod
    def save_item(cls, split: str, item: EventReasoningItem) -> None:
        file_path = os.path.join(DATASET_DIR, f"{split}_event_reasoning.jsonl")
        os.makedirs(DATASET_DIR, exist_ok=True)
        d = {
            "sentence": item.sentence,
            "event_mentions": [
                {
                    "type": ev.type.value if hasattr(ev.type, 'value') else str(ev.type),
                    "trigger": {"text": ev.trigger},
                    "arguments": [
                        {
                            "type": arg.type.value if hasattr(arg.type, 'value') else str(arg.type),
                            "text": arg.text
                        } for arg in ev.arguments
                    ]
                } for ev in item.events
            ],
            "reasoning": item.reasoning
        }
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")






class ArgumentReasoningItem(BaseModel):
    sentence: str
    event_type: EventType
    event_trigger: str
    entities: List[MentionedEntity]
    arguments: List[Argument]
    reasoning: str


class ArgumentReasoningDataset(BaseModel):
    items: List[ArgumentReasoningItem]

    def __iter__(self) -> Iterator[ArgumentReasoningItem]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> ArgumentReasoningItem:
        return self.items[index]

    def save(self, split: str) -> None:
        file_path = os.path.join(DATASET_DIR, f"{split}_argument_reasoning.jsonl")
        os.makedirs(DATASET_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            for item in self.items:
                d = {
                    "sentence": item.sentence,
                    "type": item.event_type.value if hasattr(item.event_type, 'value') else str(item.event_type),
                    "trigger": item.event_trigger,
                    "entity_mentions": [
                        {
                            "text": ent.text,
                            "type": ent.type.value if hasattr(ent.type, 'value') else str(ent.type)
                        } for ent in item.entities
                    ],
                    "arguments": [
                        {
                            "type": arg.type.value if hasattr(arg.type, 'value') else str(arg.type),
                            "text": arg.text
                        } for arg in item.arguments
                    ],
                    "reasoning": item.reasoning
                }
                f.write(json.dumps(d, ensure_ascii=False) + "\n")

    @classmethod
    def save_item(cls, split: str, item: ArgumentReasoningItem) -> None:
        file_path = os.path.join(DATASET_DIR, f"{split}_argument_reasoning.jsonl")
        os.makedirs(DATASET_DIR, exist_ok=True)
        d = {
            "sentence": item.sentence,
            "type": item.event_type.value if hasattr(item.event_type, 'value') else str(item.event_type),
            "trigger": item.event_trigger,
            "entity_mentions": [
                {
                    "text": ent.text,
                    "type": ent.type.value if hasattr(ent.type, 'value') else str(ent.type)
                } for ent in item.entities
            ],
            "arguments": [
                {
                    "type": arg.type.value if hasattr(arg.type, 'value') else str(arg.type),
                    "text": arg.text
                } for arg in item.arguments
            ],
            "reasoning": item.reasoning
        }
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")






class FullReasoningItem(BaseModel):
    sentence: str
    entities: List[MentionedEntity]
    events: List[MentionedEvent]
    reasoning: str


class FullReasoningDataset(BaseModel):
    items: List[FullReasoningItem]

    def __iter__(self) -> Iterator[FullReasoningItem]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __getitem__(self, index: int) -> FullReasoningItem:
        return self.items[index]

    def save(self, split: str) -> None:
        file_path = os.path.join(DATASET_DIR, f"{split}_full_reasoning.jsonl")
        os.makedirs(DATASET_DIR, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            for item in self.items:
                d = {
                    "sentence": item.sentence,
                    "entity_mentions": [
                        {
                            "text": ent.text,
                            "type": ent.type.value if hasattr(ent.type, 'value') else str(ent.type)
                        } for ent in item.entities
                    ],
                    "event_mentions": [
                        {
                            "type": ev.type.value if hasattr(ev.type, 'value') else str(ev.type),
                            "trigger": {"text": ev.trigger},
                            "arguments": [
                                {
                                    "type": arg.type.value if hasattr(arg.type, 'value') else str(arg.type),
                                    "text": arg.text
                                } for arg in ev.arguments
                            ]
                        } for ev in item.events
                    ],
                    "reasoning": item.reasoning
                }
                f.write(json.dumps(d, ensure_ascii=False) + "\n")

    @classmethod
    def save_item(cls, split: str, item: FullReasoningItem) -> None:
        file_path = os.path.join(DATASET_DIR, f"{split}_full_reasoning.jsonl")
        os.makedirs(DATASET_DIR, exist_ok=True)
        d = {
            "sentence": item.sentence,
            "entity_mentions": [
                {
                    "text": ent.text,
                    "type": ent.type.value if hasattr(ent.type, 'value') else str(ent.type)
                } for ent in item.entities
            ],
            "event_mentions": [
                {
                    "type": ev.type.value if hasattr(ev.type, 'value') else str(ev.type),
                    "trigger": {"text": ev.trigger},
                    "arguments": [
                        {
                            "type": arg.type.value if hasattr(arg.type, 'value') else str(arg.type),
                            "text": arg.text
                        } for arg in ev.arguments
                    ]
                } for ev in item.events
            ],
            "reasoning": item.reasoning
        }
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")





        