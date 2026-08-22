import os
from typing import Literal, Union, Optional
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
    FullModel,
    FinetunedModel
)

def find_last_checkpoint(run_dir: str) -> tuple[str, int]:
    """Finds the last checkpoint path and its step number in a run directory."""
    if not os.path.exists(run_dir):
        raise FileNotFoundError(f"Run directory not found: {run_dir}")
        
    ckpt_dirs = []
    for name in os.listdir(run_dir):
        full_path = os.path.join(run_dir, name)
        if os.path.isdir(full_path) and name.startswith("checkpoint-"):
            try:
                step = int(name.split("-")[1])
                ckpt_dirs.append((full_path, step))
            except ValueError:
                pass
                
    if not ckpt_dirs:
        raise FileNotFoundError(f"No checkpoint directories found in: {run_dir}")
        
    # Get checkpoint with maximum step
    last_ckpt = max(ckpt_dirs, key=lambda x: x[1])
    return last_ckpt[0], last_ckpt[1]


def prune_checkpoints(output_dir: str, saved_checkpoints: list, keep_limit: int = 10):
    if len(saved_checkpoints) <= keep_limit:
        return
    # Sort by loss ascending
    sorted_ckpts = sorted(saved_checkpoints, key=lambda x: x[1])
    # Keep the top keep_limit checkpoints (lowest loss)
    ckpts_to_keep = set(ckpt[0] for ckpt in sorted_ckpts[:keep_limit])
    
    # Delete the rest
    import shutil
    for ckpt_step, loss in list(saved_checkpoints):
        if ckpt_step not in ckpts_to_keep:
            ckpt_dir = os.path.join(output_dir, f"checkpoint-{ckpt_step}")
            if os.path.exists(ckpt_dir):
                print(f"Pruning checkpoint-{ckpt_step} (Loss: {loss:.4f}) to keep only the {keep_limit} lowest loss checkpoints...")
                try:
                    shutil.rmtree(ckpt_dir)
                except Exception as e:
                    print(f"Error pruning checkpoint-{ckpt_step}: {e}")
            if (ckpt_step, loss) in saved_checkpoints:
                saved_checkpoints.remove((ckpt_step, loss))


try:
    from transformers import TrainerCallback
    class CheckpointPruningCallback(TrainerCallback):
        def __init__(self, output_dir, keep_limit=10):
            self.output_dir = output_dir
            self.keep_limit = keep_limit
            self.saved_checkpoints = []
            
            # Populate existing checkpoints
            if os.path.exists(output_dir):
                for name in os.listdir(output_dir):
                    full_path = os.path.join(output_dir, name)
                    if os.path.isdir(full_path) and name.startswith("checkpoint-"):
                        try:
                            step = int(name.split("-")[1])
                            self.saved_checkpoints.append((step, 999.0))
                        except ValueError:
                            pass

        def on_save(self, args, state, control, **kwargs):
            current_step = state.global_step
            current_loss = None
            for log in reversed(state.log_history):
                if "loss" in log and log.get("step") == current_step:
                    current_loss = log["loss"]
                    break
            if current_loss is None:
                for log in reversed(state.log_history):
                    if "loss" in log:
                        current_loss = log["loss"]
                        break
            if current_loss is not None:
                self.saved_checkpoints.append((current_step, current_loss))
                prune_checkpoints(self.output_dir, self.saved_checkpoints, self.keep_limit)
except ImportError:
    pass


class Trainer:
    def __init__(self, model_name: str = "Qwen/Qwen3-4B-Instruct-2507", max_seq_length: Optional[int] = None, finetune_type: str = "lora"):
        self.model_name = model_name
        self.max_seq_length = max_seq_length
        self.finetune_type = finetune_type
        self.model = None
        
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
        
        from transformers import AutoTokenizer
        print(f"Initializing Tokenizer: {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def _initialize_model(self):
        import torch
        import unsloth
        
        use_lora = (self.finetune_type == "lora")
        
        if self.device_type == "mlx" or self.device_type == "cuda":
            from unsloth import FastLanguageModel
            print(f"Initializing FastLanguageModel ({self.device_type.upper()}) for {'LoRA' if use_lora else 'Full'} Fine-Tuning: {self.model_name} (max_seq_length={self.max_seq_length})...")
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name = self.model_name,
                max_seq_length = self.max_seq_length,
                dtype = None,               # Auto detect float16 (T4, V100) or bfloat16 (Ampere+)
                load_in_4bit = use_lora,    # Enable 4-bit quantization for LoRA
                full_finetuning = not use_lora
            )
            
            if use_lora:
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
            from transformers import AutoModelForCausalLM
            
            print(f"Initializing Standard Transformers Model ({self.device_type.upper()}) for {'LoRA' if use_lora else 'Full'} Fine-Tuning: {self.model_name} (max_seq_length={self.max_seq_length})...")
            
            load_kwargs = {}
            if self.device_type == "mps":
                load_kwargs["torch_dtype"] = torch.float16
            else:
                load_kwargs["torch_dtype"] = torch.float32
                
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                **load_kwargs
            )
            
            if self.device_type == "mps":
                self.model = self.model.to("mps")
                
            if use_lora:
                from peft import LoraConfig, get_peft_model
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
        epochs: int = 2,
        save_steps: int = 500,
        continue_run: Optional[str] = None
    ) -> Union[EntityExtractorModel, EventExtractorModel, ArgumentAssignerModel, FullModel]:
        # Determine the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        
        resume_from_checkpoint_dir = None
        last_step_num = 0

        if continue_run:
            # Resolve directory
            if os.path.exists(continue_run):
                output_dir = os.path.abspath(continue_run)
            else:
                output_dir = os.path.abspath(os.path.join(project_root, "checkpoints", continue_run))
                
            if not os.path.exists(output_dir):
                raise FileNotFoundError(f"Run directory not found: {continue_run}")
                
            resume_from_checkpoint_dir, last_step_num = find_last_checkpoint(output_dir)
            print(f"Resuming training. Found last checkpoint: {resume_from_checkpoint_dir} (step {last_step_num})")
        else:
            # Generate new directory name
            from datetime import datetime
            run_name = f"run--{datetime.now().strftime('%Y-%m-%d--%H-%M-%S')}"
            output_dir = os.path.join(project_root, "checkpoints", run_name)
            
        final_model_dir = os.path.join(output_dir, "final")
        
        # Create output and final model directories
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(final_model_dir, exist_ok=True)

        formatted_dataset = convert_to_train_dataset(dataset, phase, self.tokenizer)
        print(f"Successfully processed and formatted {len(formatted_dataset)} samples.")
        
        # Print estimated steps for visibility
        effective_batch_size = 4  # batch_size=1 * grad_accum=4
        estimated_steps_per_epoch = len(formatted_dataset) // effective_batch_size
        estimated_total_steps = estimated_steps_per_epoch * epochs
        print(f"Estimated steps: ~{estimated_steps_per_epoch}/epoch × {epochs} epochs = ~{estimated_total_steps} total steps")
        
        if continue_run:
            if last_step_num >= estimated_total_steps:
                raise ValueError(
                    f"Run already completed {last_step_num} steps, which is >= estimated total steps ({estimated_total_steps}) for {epochs} epochs. "
                    f"Please increase epochs to continue training."
                )
        
        # Calculate dynamic max_seq_length based on dataset token counts
        print("Calculating dynamic max_seq_length based on dataset token counts...")
        encodings = self.tokenizer(list(formatted_dataset["text"]), add_special_tokens=False, return_attention_mask=False)
        token_lengths = [len(ids) for ids in encodings["input_ids"]]
        max_dataset_tokens = max(token_lengths) if token_lengths else 0
        
        # Find the next power of 2 starting at 1024
        dynamic_seq_len = 1024
        while dynamic_seq_len < max_dataset_tokens:
            dynamic_seq_len *= 2
            
        print(f"Dataset token stats - Max tokens: {max_dataset_tokens}, Selected max_seq_length: {dynamic_seq_len}")
        self.max_seq_length = dynamic_seq_len
        
        # Initialize model with the calculated max_seq_length
        self._initialize_model()
        
        # Load weights from checkpoint if resuming under MLX
        if resume_from_checkpoint_dir and self.device_type == "mlx":
            adapters_file = os.path.join(resume_from_checkpoint_dir, "adapters.safetensors")
            if os.path.exists(adapters_file):
                print(f"Resuming MLX training: loading weights from {adapters_file}...")
                import mlx.core as mx
                from mlx.utils import tree_unflatten
                self.model.update(tree_unflatten(list(mx.load(adapters_file).items())))
            else:
                print(f"Warning: Checkpoint file {adapters_file} not found. Starting from scratch.")

        print(f"Checkpoints directory for this run: {output_dir}")
        
        if self.device_type == "mlx":
            from unsloth import MLXTrainer, MLXTrainingConfig
            print("Preparing MLXTrainer for macOS/MLX...")
            
            # When resuming we need max_steps (remaining); otherwise use num_train_epochs
            if last_step_num > 0:
                remaining_steps = max(1, estimated_total_steps - last_step_num)
                print(f"Resuming: {last_step_num} steps done, {remaining_steps} steps remaining.")
                mlx_epoch_or_steps = dict(max_steps=remaining_steps, num_train_epochs=-1)
            else:
                mlx_epoch_or_steps = dict(max_steps=-1, num_train_epochs=epochs)
            
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
                    **mlx_epoch_or_steps,
                    learning_rate = 2e-5,
                    optim = "adamw",
                    weight_decay = 0.01,
                    lr_scheduler_type = "linear",
                    seed = 3407,
                    output_dir = output_dir,
                    dataset_num_proc = 4,
                    logging_steps = 10,
                    save_steps = 0,             # Disable built-in saving; we do it in callback
                    save_total_limit = -1
                )
            )
            
            # Setup manual checkpoint saving and pruning for MLX
            saved_checkpoints = []
            
            # Populate already existing checkpoints if resuming
            if last_step_num > 0:
                for name in os.listdir(output_dir):
                    full_path = os.path.join(output_dir, name)
                    if os.path.isdir(full_path) and name.startswith("checkpoint-"):
                        try:
                            step = int(name.split("-")[1])
                            saved_checkpoints.append((step, 999.0))
                        except ValueError:
                            pass

            def mlx_step_callback(current_step, total_steps, train_loss, lr, tok_s, mem, elapsed, tokens, grad):
                actual_step = current_step + last_step_num
                if current_step % save_steps == 0 or current_step == total_steps:
                    ckpt_dir = os.path.join(output_dir, f"checkpoint-{actual_step}")
                    print(f"\nSaving checkpoint to {ckpt_dir}...")
                    trainer.save_model(ckpt_dir)
                    
                    saved_checkpoints.append((actual_step, train_loss))
                    prune_checkpoints(output_dir, saved_checkpoints, keep_limit=10)

            trainer._step_callbacks.append(mlx_step_callback)
            
            print("Starting Unsloth MLX LoRA Fine-Tuning...")
            trainer.train()
        else:
            from trl import SFTTrainer, SFTConfig
            print(f"Preparing SFTTrainer for {self.device_type.upper()}...")
            
            import torch
            has_bf16 = False
            if self.device_type == "cuda":
                has_bf16 = torch.cuda.is_bf16_supported()
                
            callbacks = [CheckpointPruningCallback(output_dir, 10)]
                
            trainer = SFTTrainer(
                model = self.model,
                processing_class = self.tokenizer,
                train_dataset = formatted_dataset,
                callbacks = callbacks,
                args = SFTConfig(
                    dataset_text_field = "text",
                    max_seq_length = self.max_seq_length,
                    packing = False,
                    per_device_train_batch_size = 1,
                    gradient_accumulation_steps = 4,
                    warmup_steps = 100,
                    num_train_epochs = epochs,
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
                    fp16 = (self.device_type == "cuda" and not has_bf16),
                    bf16 = (self.device_type == "cuda" and has_bf16),
                )
            )
            print(f"Starting LoRA Fine-Tuning using SFTTrainer ({self.device_type.upper()})...")
            if resume_from_checkpoint_dir:
                trainer.train(resume_from_checkpoint=resume_from_checkpoint_dir)
            else:
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
    ) -> Union[EntityExtractorModel, EventExtractorModel, ArgumentAssignerModel, FullModel]:
        if phase == "entity":
            return EntityExtractorModel(checkpoint_dir, self.max_seq_length)
        elif phase == "event":
            return EventExtractorModel(checkpoint_dir, self.max_seq_length)
        elif phase == "argument":
            return ArgumentAssignerModel(checkpoint_dir, self.max_seq_length)
        elif phase == "full":
            return FullModel(checkpoint_dir, self.max_seq_length)
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

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ckpt_path = os.path.join(project_root, 'checkpoints', 'run--2026-06-24--13-47-27', 'final')
    finetuned_model = EntityExtractorModel(ckpt_path)
    finetuned_model.evaluate(dataset=test_dataset)





