import os
from typing import Literal, Union
from apps.helpers.dataset_loader import (
    load_base_dataset,
    load_entity_reasoning_dataset,
    load_event_reasoning_dataset,
    load_argument_reasoning_dataset,
    load_full_reasoning_dataset,
    Dataset
)
from apps.trainers.dataset_converter import convert_to_train_dataset
from apps.models import (
    EntityReasoningDataset,
    EventReasoningDataset,
    ArgumentReasoningDataset,
    FullReasoningDataset
)
from apps.trainers.inference_models import (
    EntityExtractorModel,
    EventExtractorModel,
    ArgumentAssignerModel,
    FullPipelineModel,
    FinetunedModel
)

class Trainer:
    def __init__(self, model_name: str = "Qwen/Qwen3-4B-Instruct-2507", max_seq_length: int = 2048):
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        
        import torch
        import unsloth
        
        is_mlx = getattr(unsloth, "_IS_MLX", False)
        if is_mlx:
            self.device_type = "mlx"
        elif torch.cuda.is_available():
            self.device_type = "cuda"
        elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            self.device_type = "mps"
        else:
            self.device_type = "cpu"
            
        print(f"Detected training device: {self.device_type.upper()}")
        
        if self.device_type == "mlx" or self.device_type == "cuda":
            from unsloth import FastLanguageModel
            print(f"Initializing FastLanguageModel ({self.device_type.upper()}) for LoRA Fine-Tuning: {model_name}...")
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name = model_name,
                max_seq_length = max_seq_length,
                dtype = None,               # Auto detect float16 (T4, V100) or bfloat16 (Ampere+)
                load_in_4bit = True,        # Enable 4-bit quantization for LoRA
                full_finetuning = False     # False for LoRA
            )
            # Apply PEFT LoRA wrapper
            self.model = FastLanguageModel.get_peft_model(
                self.model,
                r = 16,
                target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                                  "gate_proj", "up_proj", "down_proj"],
                lora_alpha = 16,
                lora_dropout = 0,
                bias = "none",
                use_gradient_checkpointing = "unsloth",
                random_state = 3407,
                use_rslora = False,
                loftq_config = None,
            )
        else:
            # Fallback to standard HuggingFace for MPS or CPU
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from peft import LoraConfig, get_peft_model
            
            print(f"Initializing Standard Transformers Model ({self.device_type.upper()}) for LoRA Fine-Tuning: {model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            load_kwargs = {}
            if self.device_type == "mps":
                load_kwargs["torch_dtype"] = torch.float16
            else:
                load_kwargs["torch_dtype"] = torch.float32
                
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                **load_kwargs
            )
            
            if self.device_type == "mps":
                self.model = self.model.to("mps")
                
            peft_config = LoraConfig(
                r = 16,
                lora_alpha = 16,
                target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                                  "gate_proj", "up_proj", "down_proj"],
                lora_dropout = 0.05,
                bias = "none",
                task_type = "CAUSAL_LM"
            )
            self.model = get_peft_model(self.model, peft_config)

    def train(
        self, 
        dataset: Union[EntityReasoningDataset, EventReasoningDataset, ArgumentReasoningDataset, FullReasoningDataset],
        phase: Literal["entity", "event", "argument", "full"], 
        max_steps: int = 600,
        save_steps: int = 50
    ) -> Union[EntityExtractorModel, EventExtractorModel, ArgumentAssignerModel, FullPipelineModel]:
        # Determine the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        
        # Generate directory: checkpoints/run--yyyy-mm-dd--hh-mm-ss
        from datetime import datetime
        run_name = f"run--{datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}"
        output_dir = os.path.join(project_root, "checkpoints", run_name)
        final_model_dir = os.path.join(output_dir, "final")
        
        # Create output and final model directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(final_model_dir, exist_ok=True)

        formatted_dataset = convert_to_train_dataset(dataset, phase, self.tokenizer)
        print(f"Successfully processed and formatted {len(formatted_dataset)} samples.")
        
        print(f"Checkpoints directory for this run: {output_dir}")
        
        if self.device_type == "mlx":
            from unsloth import MLXTrainer, MLXTrainingConfig
            print("Preparing MLXTrainer for macOS/MLX...")
            trainer = MLXTrainer(
                model = self.model,
                tokenizer = self.tokenizer,
                train_dataset = formatted_dataset,
                args = MLXTrainingConfig(
                    dataset_text_field = "text",
                    max_seq_length = self.max_seq_length,
                    packing = False,
                    per_device_train_batch_size = 1,
                    gradient_accumulation_steps = 4,
                    warmup_steps = 100,
                    max_steps = max_steps,
                    learning_rate = 2e-5,
                    optim = "adamw",
                    weight_decay = 0.01,
                    lr_scheduler_type = "linear",
                    seed = 3407,
                    output_dir = output_dir,
                    dataset_num_proc = 4,
                    logging_steps = 10,
                    save_steps = save_steps,
                    save_total_limit = 5
                )
            )
            print("Starting Unsloth MLX LoRA Fine-Tuning...")
            trainer.train()
        else:
            from trl import SFTTrainer, SFTConfig
            print(f"Preparing SFTTrainer for {self.device_type.upper()}...")
            
            import torch
            has_bf16 = False
            if self.device_type == "cuda":
                has_bf16 = torch.cuda.is_bf16_supported()
                
            trainer = SFTTrainer(
                model = self.model,
                processing_class = self.tokenizer,
                train_dataset = formatted_dataset,
                args = SFTConfig(
                    dataset_text_field = "text",
                    max_seq_length = self.max_seq_length,
                    packing = False,
                    per_device_train_batch_size = 1,
                    gradient_accumulation_steps = 4,
                    warmup_steps = 100,
                    max_steps = max_steps,
                    learning_rate = 2e-5,
                    optim = "adamw_torch",
                    weight_decay = 0.01,
                    lr_scheduler_type = "linear",
                    seed = 3407,
                    output_dir = output_dir,
                    dataset_num_proc = 4,
                    logging_steps = 10,
                    save_strategy = "steps",
                    save_steps = save_steps,
                    save_total_limit = 5,
                    fp16 = (self.device_type == "cuda" and not has_bf16),
                    bf16 = (self.device_type == "cuda" and has_bf16),
                    use_mps_device = (self.device_type == "mps"),
                )
            )
            print(f"Starting LoRA Fine-Tuning using SFTTrainer ({self.device_type.upper()})...")
            trainer.train()
        
        print(f"Saving final model parameters to: {final_model_dir}...")
        if hasattr(self.model, "save_pretrained_merged"):
            self.model.save_pretrained_merged(final_model_dir, tokenizer=self.tokenizer, save_method="merged_16bit")
        else:
            self.model.save_pretrained(final_model_dir)
            self.tokenizer.save_pretrained(final_model_dir)
        print("Training finished and model saved successfully! 🎉")


        # Unload trainer model & tokenizer to free RAM/VRAM
        print("Unloading trainer model and releasing resources...")
        self.model = None
        self.tokenizer = None
        del trainer

        import gc
        gc.collect()
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            elif hasattr(torch, "mps") and torch.mps.is_available():
                torch.mps.empty_cache()
        except Exception:
            pass

        try:
            import mlx.core as mx
            if hasattr(mx, "clear_cache"):
                mx.clear_cache()
            else:
                mx.metal.clear_cache()
        except Exception:
            pass

        print(f"Loading finetuned model checkpoint from {final_model_dir}...")
        return self.get_inference_model(phase, final_model_dir)

    def get_inference_model(
        self,
        phase: Literal["entity", "event", "argument", "full"],
        checkpoint_dir: str
    ) -> Union[EntityExtractorModel, EventExtractorModel, ArgumentAssignerModel, FullPipelineModel]:
        if phase == "entity":
            return EntityExtractorModel(checkpoint_dir, self.max_seq_length)
        elif phase == "event":
            return EventExtractorModel(checkpoint_dir, self.max_seq_length)
        elif phase == "argument":
            return ArgumentAssignerModel(checkpoint_dir, self.max_seq_length)
        elif phase == "full":
            return FullPipelineModel(checkpoint_dir, self.max_seq_length)
        else:
            raise ValueError(f"Invalid phase: {phase}")


if __name__ == "__main__":
    # Test block to run a quick test training session
    print("=== Testing Trainer Pipeline ===")
    phase = "entity"
    print(f"Loading training dataset for phase: {phase}...")
    if phase == "entity":
        train_dataset = load_entity_reasoning_dataset("train")
    elif phase == "event":
        train_dataset = load_event_reasoning_dataset("train")
    elif phase == "argument":
        train_dataset = load_argument_reasoning_dataset("train")
    elif phase == "full":
        train_dataset = load_full_reasoning_dataset("train")
    else:
        raise ValueError(f"Invalid phase: {phase}")

    test_dataset = load_base_dataset("test")
    
    # trainer = Trainer(model_name="Qwen/Qwen3-4B-Instruct-2507", max_seq_length=2048)
    
    # # We run for a very small number of steps (1 step) to test training flow
    # print("Starting a 1-step test training for phase 'entity'...")
    # finetuned_model = trainer.train(train_dataset, phase="entity", max_steps=1, save_steps=1)
    # print(f"Success! Finetuned model loaded successfully: {finetuned_model}")

    finetuned_model = EntityExtractorModel('/Users/dagoras/Documents/workspace/distant-supervision-ee/checkpoints/run--2026-06-24--13-47-27/final')
    finetuned_model.evaluate(dataset=test_dataset)





