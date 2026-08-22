import sys

sys.path.append('./')

import argparse
import sys
import os
from apps.helpers.dataset_loader import (
    load_base_dataset,
    load_entity_reasoning_dataset,
    load_event_reasoning_dataset,
    load_argument_reasoning_dataset,
    load_full_reasoning_dataset
)
from apps.models import (
    DATASET_DIR,
    EntityReasoningDataset,
    EventReasoningDataset,
    ArgumentReasoningDataset,
    FullReasoningDataset
)
from apps.data_builder import (
    EntityBuilder,
    EventBuilder,
    ArgumentBuilder,
    FullBuilder
)

def build_data(phase: str, n_jobs: int):
    print(f"=== Starting Dataset Build for phase: {phase} ===")
    print(f"Parallel workers (n_jobs): {n_jobs}")
    
    for split in ["train", "test"]:
        print(f"\n--- Loading base dataset split: {split} ---")
        try:
            base_dataset = load_base_dataset(split)
        except FileNotFoundError as e:
            print(f"Warning: {e}. Skipping this split.")
            continue
            
        print(f"Loaded {len(base_dataset)} base samples.")
        
        # Determine existing items in target file to skip them and support resume
        existing_items = []
        file_path = os.path.join(DATASET_DIR, f"{split}_{phase}_reasoning.jsonl")
        
        if os.path.exists(file_path):
            try:
                if phase == "entity":
                    existing_items = list(load_entity_reasoning_dataset(split).items)
                elif phase == "event":
                    existing_items = list(load_event_reasoning_dataset(split).items)
                elif phase == "argument":
                    existing_items = list(load_argument_reasoning_dataset(split).items)
                elif phase == "full":
                    existing_items = list(load_full_reasoning_dataset(split).items)
                print(f"Resuming: Loaded {len(existing_items)} existing reasoning items from {file_path}.")
            except Exception as e:
                print(f"Warning: Failed to load existing reasoning items from {file_path} ({e}). Starting fresh.")
                existing_items = []
                if os.path.exists(file_path):
                    os.remove(file_path)
                    
        existing_count = len(existing_items)
        
        # Clear/truncate target file first to start fresh (ONLY IF WE ARE NOT RESUMING!)
        if existing_count == 0 and os.path.exists(file_path):
            os.remove(file_path)
        
        if phase == "entity":
            builder = EntityBuilder()
            batch_items = [(item.sentence, item.entities) for item in base_dataset]
            print(f"Total candidate items: {len(batch_items)}")
            if existing_count >= len(batch_items):
                print(f"All {len(batch_items)} items for {split} split are already processed. Skipping.")
                continue
            
            if existing_count > 0:
                batch_items = batch_items[existing_count:]
                print(f"Resuming. Slicing batch_items to skip first {existing_count} items. Remaining: {len(batch_items)}")
                
            print(f"Generating reasoning for {len(batch_items)} items...")
            new_reasoning_items = builder.build_batch(
                batch_items, 
                max_workers=n_jobs,
                callback=lambda item: EntityReasoningDataset.save_item(split, item)
            )
            dataset = EntityReasoningDataset(items=existing_items + new_reasoning_items)
            dataset.save(split)
            print(f"Saved entity reasoning dataset for split: {split}")
            
        elif phase == "event":
            builder = EventBuilder()
            batch_items = [(item.sentence, item.events) for item in base_dataset]
            print(f"Total candidate items: {len(batch_items)}")
            if existing_count >= len(batch_items):
                print(f"All {len(batch_items)} items for {split} split are already processed. Skipping.")
                continue
            
            if existing_count > 0:
                batch_items = batch_items[existing_count:]
                print(f"Resuming. Slicing batch_items to skip first {existing_count} items. Remaining: {len(batch_items)}")
                
            print(f"Generating reasoning for {len(batch_items)} items...")
            new_reasoning_items = builder.build_batch(
                batch_items, 
                max_workers=n_jobs,
                callback=lambda item: EventReasoningDataset.save_item(split, item)
            )
            dataset = EventReasoningDataset(items=existing_items + new_reasoning_items)
            dataset.save(split)
            print(f"Saved event reasoning dataset for split: {split}")
            
        elif phase == "argument":
            builder = ArgumentBuilder()
            batch_items = []
            for item in base_dataset:
                if not item.events or not item.entities:
                    continue
                for ev in item.events:
                    batch_items.append((
                        item.sentence,
                        ev.type,
                        ev.trigger,
                        item.entities,
                        ev.arguments
                    ))
            print(f"Total candidate items: {len(batch_items)}")
            if existing_count >= len(batch_items):
                print(f"All {len(batch_items)} items for {split} split are already processed. Skipping.")
                continue
            
            if existing_count > 0:
                batch_items = batch_items[existing_count:]
                print(f"Resuming. Slicing batch_items to skip first {existing_count} items. Remaining: {len(batch_items)}")
                
            print(f"Generating reasoning for {len(batch_items)} event-argument items...")
            new_reasoning_items = builder.build_batch(
                batch_items, 
                max_workers=n_jobs,
                callback=lambda item: ArgumentReasoningDataset.save_item(split, item)
            )
            dataset = ArgumentReasoningDataset(items=existing_items + new_reasoning_items)
            dataset.save(split)
            print(f"Saved argument reasoning dataset for split: {split}")
            
        elif phase == "full":
            builder = FullBuilder()
            batch_items = [(item.sentence, item.entities, item.events) for item in base_dataset]
            print(f"Total candidate items: {len(batch_items)}")
            if existing_count >= len(batch_items):
                print(f"All {len(batch_items)} items for {split} split are already processed. Skipping.")
                continue
            
            if existing_count > 0:
                batch_items = batch_items[existing_count:]
                print(f"Resuming. Slicing batch_items to skip first {existing_count} items. Remaining: {len(batch_items)}")
                
            print(f"Generating reasoning for {len(batch_items)} items...")
            new_reasoning_items = builder.build_batch(
                batch_items, 
                max_workers=n_jobs,
                callback=lambda item: FullReasoningDataset.save_item(split, item)
            )
            dataset = FullReasoningDataset(items=existing_items + new_reasoning_items)
            dataset.save(split)
            print(f"Saved full reasoning dataset for split: {split}")
            
        else:
            raise ValueError(f"Invalid build phase: {phase}")


def run_eval(eval_model: str, sample: float, n_jobs: int, options: list, csv_output: str):
    include_hints = "include_hints" in options
    few_shot = "few_shot" in options

    print(f"=== Starting Evaluation for model: {eval_model} ===")
    print(f"Sample rate: {sample}, n_jobs: {n_jobs}, include_hints: {include_hints}, few_shot: {few_shot}")

    from apps.evaluators.eval_runner import run_evaluation
    run_evaluation(
        eval_model=eval_model,
        sample=sample,
        n_jobs=n_jobs,
        include_hints=include_hints,
        few_shot=few_shot,
        csv_path=csv_output,
    )


def run_training(phase: str, model_name: str, epochs: int, save_steps: int, max_seq_length: int, finetune_type: str, continue_run: str = None):
    print(f"=== Starting Training for phase: {phase} ===")
    print(f"Base Model: {model_name}")
    print(f"Finetune Type: {finetune_type}")
    print(f"Epochs: {epochs}, Save Steps: {save_steps}")
    if continue_run:
        print(f"Resuming Run: {continue_run}")
    
    if phase == "entity":
        train_dataset = load_entity_reasoning_dataset("train")
    elif phase == "event":
        train_dataset = load_event_reasoning_dataset("train")
    elif phase == "argument":
        train_dataset = load_argument_reasoning_dataset("train")
    elif phase == "full":
        train_dataset = load_full_reasoning_dataset("train")
    else:
        raise ValueError(f"Invalid training phase: {phase}")
        
    from apps.trainers.trainer import Trainer
    trainer = Trainer(model_name=model_name, max_seq_length=max_seq_length, finetune_type=finetune_type)
    finetuned_model = trainer.train(
        dataset=train_dataset,
        phase=phase,
        epochs=epochs,
        save_steps=save_steps,
        continue_run=continue_run
    )
    print(f"Successfully trained and loaded finetuned model: {finetuned_model}")


def main():
    parser = argparse.ArgumentParser(description="EE Distant Supervision Main Runner")
    parser.add_argument(
        "--build_data",
        choices=["entity", "event", "argument", "full"],
        help="Select the phase of dataset to build: entity, event, argument, or full"
    )
    parser.add_argument(
        "--n_jobs",
        type=int,
        default=5,
        help="Number of parallel workers for builder queries (default: 5)"
    )
    parser.add_argument(
        "--train",
        choices=["entity", "event", "argument", "full"],
        help="Select the phase to train: entity, event, argument, or full"
    )
    parser.add_argument(
        "--model_name",
        type=str,
        default="Qwen/Qwen3-4B-Instruct-2507",
        help="Base model to finetune (default: Qwen/Qwen3-4B-Instruct-2507)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=2,
        help="Number of training epochs (default: 2)"
    )
    parser.add_argument(
        "--save_steps",
        type=int,
        default=500,
        help="Save steps interval (default: 500)"
    )
    parser.add_argument(
        "--max_seq_length",
        type=int,
        default=2048,
        help="Maximum sequence length (default: 2048)"
    )
    parser.add_argument(
        "--finetune_type",
        choices=["lora", "full"],
        default="lora",
        help="Finetuning type: lora or full (default: lora)"
    )
    parser.add_argument(
        "--continue",
        dest="continue_run",
        type=str,
        default=None,
        help="Continue training from a run folder name or path (e.g. run--2026-07-09--09-34-18)"
    )
    parser.add_argument(
        "--eval_model",
        type=str,
        default=None,
        help="Model to evaluate: an OpenRouter model identifier, or an absolute/relative path to a finetuned checkpoint"
    )
    parser.add_argument(
        "--sample",
        type=float,
        default=1.0,
        help="Sample rate of the test set to evaluate, as a float ratio in (0, 1] (default: 1.0)"
    )
    parser.add_argument(
        "--options",
        nargs="*",
        choices=["include_hints", "few_shot"],
        default=[],
        help="Extra system prompt options for OpenRouter-based evaluation: include_hints and/or few_shot "
             "(ignored for local finetuned checkpoints, which always use their fixed finetuned system prompt)"
    )
    parser.add_argument(
        "--csv_output",
        type=str,
        default="eval_results.csv",
        help="Path to the CSV file eval results are appended to (default: eval_results.csv)"
    )

    args = parser.parse_args()

    if args.build_data:
        build_data(args.build_data, args.n_jobs)
    elif args.eval_model:
        run_eval(
            eval_model=args.eval_model,
            sample=args.sample,
            n_jobs=args.n_jobs,
            options=args.options,
            csv_output=args.csv_output
        )
    elif args.train:
        run_training(
            phase=args.train,
            model_name=args.model_name,
            epochs=args.epochs,
            save_steps=args.save_steps,
            max_seq_length=args.max_seq_length,
            finetune_type=args.finetune_type,
            continue_run=args.continue_run
        )
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
