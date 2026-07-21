import argparse
import sys
from pathlib import Path
from apps.trainers.inference_models import FullModel

def main():
    parser = argparse.ArgumentParser(description="Inference Script for Finetuned EE Model")
    parser.add_argument(
        "--checkpoint",
        type=str,
        default=str(Path(__file__).resolve().parent / "checkpoints" / "run--2026-07-09--09-34-18" / "final"),
        help="Path to the finetuned model directory (default: latest run final/)"
    )
    parser.add_argument(
        "--sentence",
        type=str,
        default="Công ty TNHH MTV Xổ số Kiến thiết An Giang đã đóng góp 31,1 tỷ đồng cho Liên đoàn Lao động tỉnh.",
        help="Sentence to run inference on"
    )
    
    args = parser.parse_args()
    
    print(f"Loading finetuned model from: {args.checkpoint}...")
    try:
        model = FullModel(checkpoint=args.checkpoint)
    except Exception as e:
        print(f"Error loading model: {e}", file=sys.stderr)
        print("Please check if the checkpoint path is correct.", file=sys.stderr)
        sys.exit(1)
        
    print("\nRunning inference...")
    print(f"Input Sentence: {args.sentence}\n")
    
    # Run extractor
    predicted = model.infer(args.sentence)
    
    if predicted is None:
        print("Extraction failed.")
        sys.exit(1)
        
    # Print formatted output
    print("=== Extracted Entities ===")
    if not predicted.entities:
        print("No entities found.")
    for idx, ent in enumerate(predicted.entities, 1):
        print(f"{idx}. {ent.text} ({ent.type.value if hasattr(ent.type, 'value') else ent.type})")
        
    print("\n=== Extracted Events ===")
    if not predicted.events:
        print("No events found.")
    for idx, ev in enumerate(predicted.events, 1):
        print(f"{idx}. Type: {ev.type.value if hasattr(ev.type, 'value') else ev.type} | Trigger: '{ev.trigger}'")
        if ev.arguments:
            print("   Arguments:")
            for arg in ev.arguments:
                print(f"     - {arg.text} ({arg.type.value if hasattr(arg.type, 'value') else arg.type})")

if __name__ == "__main__":
    main()
