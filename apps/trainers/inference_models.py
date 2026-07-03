from typing import List, Tuple, Union, Optional, Dict, Any
from unsloth import FastLanguageModel
from apps.helpers.llm_caller import parse_llm_json
from apps.models import (
    ExtractedEntity,
    ExtractedEvent,
    AssignedEvent,
    PredictedItem
)
from apps.extractors.entity_extractor import EntityExtractor
from apps.extractors.event_extractor import EventExtractor
from apps.extractors.argument_assigner import ArgumentAssigner
from apps.extractors.full_extractor import FullExtractor

from apps.evaluators.entity_evaluator import EntityEvaluator
from apps.evaluators.event_evaluator import EventEvaluator
from apps.evaluators.argument_evaluator import ArgumentEvaluator
from apps.evaluators.full_evaluator import FullEvaluator

class FinetunedModel:
    def __init__(self, checkpoint: str, max_seq_length: int = 2048, **kwargs):
        self.checkpoint = checkpoint
        print(f"Loading FinetunedModel checkpoint: {checkpoint}...")
        
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
            
        print(f"Detected inference device: {self.device_type.upper()}")
        
        if self.device_type == "mlx" or self.device_type == "cuda":
            from unsloth import FastLanguageModel
            self.model, self.tokenizer = FastLanguageModel.from_pretrained(
                model_name = checkpoint,
                max_seq_length = max_seq_length,
                dtype = None,
                load_in_4bit = False,
            )
            FastLanguageModel.for_inference(self.model)
        else:
            # Fallback to standard HuggingFace for MPS or CPU
            from transformers import AutoModelForCausalLM, AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(checkpoint)
            
            load_kwargs = {}
            if self.device_type == "mps":
                load_kwargs["torch_dtype"] = torch.float16
            else:
                load_kwargs["torch_dtype"] = torch.float32
                
            self.model = AutoModelForCausalLM.from_pretrained(
                checkpoint,
                **load_kwargs
            )
            if self.device_type == "mps":
                self.model = self.model.to("mps")
            self.model.eval()

    def _llm_call(self, system_prompt: str, user_prompt: str, **kwargs) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        
        import unsloth
        is_mlx = getattr(unsloth, "_IS_MLX", False)
        
        if is_mlx:
            from mlx_lm import generate
            out_str = generate(self.model, self.tokenizer, prompt, verbose=False, max_tokens=512)
        else:
            # PyTorch / CUDA / MPS / CPU generation
            inputs = self.tokenizer([prompt], return_tensors = "pt")
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            outputs = self.model.generate(**inputs, max_new_tokens = 512, use_cache = True)
            prompt_len = inputs["input_ids"].shape[1]
            out_str = self.tokenizer.decode(outputs[0][prompt_len:], skip_special_tokens = True)
            
        return parse_llm_json(out_str)

    def unload(self):
        if hasattr(self, "model") and self.model is not None:
            print(f"Unloading model weights for checkpoint: {self.checkpoint}...")
            self.model = None
        if hasattr(self, "tokenizer") and self.tokenizer is not None:
            self.tokenizer = None

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

    def __del__(self):
        try:
            self.unload()
        except Exception:
            pass



class EntityExtractorModel(FinetunedModel):
    def __init__(self, checkpoint: str, max_seq_length: int = 2048):
        super().__init__(checkpoint, max_seq_length)
        self.extractor = EntityExtractor(llm_caller_func=self._llm_call, few_shot=False)
        self.evaluator = EntityEvaluator(extractor=self.extractor)

    def infer(self, sentence: str) -> List[ExtractedEntity]:
        return self.extractor.extract(sentence)

    def evaluate(self, **kwargs):
        return self.evaluator.evaluate(**kwargs)


class EventExtractorModel(FinetunedModel):
    def __init__(self, checkpoint: str, max_seq_length: int = 2048):
        super().__init__(checkpoint, max_seq_length)
        self.extractor = EventExtractor(llm_caller_func=self._llm_call, few_shot=False)
        self.evaluator = EventEvaluator(extractor=self.extractor)

    def infer(self, sentence: str) -> List[ExtractedEvent]:
        return self.extractor.extract(sentence)

    def evaluate(self, **kwargs):
        return self.evaluator.evaluate(**kwargs)


class ArgumentAssignerModel(FinetunedModel):
    def __init__(self, checkpoint: str, max_seq_length: int = 2048):
        super().__init__(checkpoint, max_seq_length)
        self.assigner = ArgumentAssigner(llm_caller_func=self._llm_call, few_shot=False)
        self.evaluator = ArgumentEvaluator(assigner=self.assigner)

    def infer(self, sentence: str, event: ExtractedEvent, entities: List[ExtractedEntity]) -> Optional[AssignedEvent]:
        return self.assigner.assign(sentence, event, entities)

    def evaluate(self, **kwargs):
        return self.evaluator.evaluate(**kwargs)


class FullPipelineModel(FinetunedModel):
    def __init__(self, checkpoint: str, max_seq_length: int = 2048):
        super().__init__(checkpoint, max_seq_length)
        self.extractor = FullExtractor(llm_caller_func=self._llm_call, few_shot=False)
        self.evaluator = FullEvaluator(extractor=self.extractor)

    def infer(self, sentence: str) -> Optional[PredictedItem]:
        return self.extractor.extract(sentence)

    def evaluate(self, **kwargs):
        return self.evaluator.evaluate(**kwargs)