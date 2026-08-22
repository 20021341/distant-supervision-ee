from apps.trainers.inference_models import FullModel
from apps.helpers.dataset_loader import load_base_dataset

model = FullModel("checkpoints/run--2026-07-14--09-34-18/final")
dataset = load_base_dataset("train")

# Khi chạy lệnh này, tqdm sẽ được tự động hiển thị:
model.evaluate(dataset=dataset, sample=20)
