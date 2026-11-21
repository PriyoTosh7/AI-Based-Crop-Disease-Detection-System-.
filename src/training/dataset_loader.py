"""EfficientNet-B3 data loaders for the existing processed dataset."""
import os
from pathlib import Path

import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

PROJECT_DIR = Path(__file__).resolve().parents[2]
_raw_data_dir = Path(os.getenv("PV_PROCESSED_DIR", str(PROJECT_DIR / "dataset" / "processed"))).expanduser()
DATA_DIR = _raw_data_dir if _raw_data_dir.is_absolute() else (PROJECT_DIR / _raw_data_dir).resolve()
IMG_SIZE = 300
BATCH_SIZE = int(os.getenv("PV_BATCH_SIZE", "32"))
NUM_WORKERS = int(os.getenv("PV_NUM_WORKERS", "0" if os.name == "nt" else "2"))
PIN_MEMORY = torch.cuda.is_available()
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

train_transform = transforms.Compose([
    transforms.RandomResizedCrop(IMG_SIZE, scale=(0.85, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(15),
    transforms.ColorJitter(brightness=0.15, contrast=0.15, saturation=0.15),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD),
])
val_test_transform = transforms.Compose([
    transforms.Resize(320),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD),
])

for split in ("train", "val", "test"):
    if not (DATA_DIR / split).is_dir():
        raise FileNotFoundError(
            f"Processed {split!r} split not found: {DATA_DIR / split}. "
            "Run `python -m src.data.prepare_dataset --dry-run` first, inspect the report, "
            "then run it without --dry-run to create splits."
        )

train_dataset = datasets.ImageFolder(DATA_DIR / "train", transform=train_transform)
val_dataset = datasets.ImageFolder(DATA_DIR / "val", transform=val_test_transform)
test_dataset = datasets.ImageFolder(DATA_DIR / "test", transform=val_test_transform)

if train_dataset.class_to_idx != val_dataset.class_to_idx or train_dataset.class_to_idx != test_dataset.class_to_idx:
    raise ValueError("Train/validation/test class mappings differ.")

class_names = train_dataset.classes
num_classes = len(class_names)
if num_classes != 39:
    raise ValueError(f"Expected 39 dataset classes, found {num_classes}.")

checkpoint_path = Path(os.getenv("PV_CHECKPOINT_PATH", str(PROJECT_DIR / "checkpoints" / "best_finetuned_efficientnet_b3.pth"))).expanduser()
if not checkpoint_path.is_absolute():
    checkpoint_path = (PROJECT_DIR / checkpoint_path).resolve()
if checkpoint_path.is_file():
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
    if list(checkpoint.get("class_names", [])) != class_names:
        raise ValueError("Dataset class order does not match the trained checkpoint class order.")

loader_options = {
    "batch_size": BATCH_SIZE,
    "num_workers": NUM_WORKERS,
    "pin_memory": PIN_MEMORY,
    "persistent_workers": NUM_WORKERS > 0,
}
train_loader = DataLoader(train_dataset, shuffle=True, **loader_options)
val_loader = DataLoader(val_dataset, shuffle=False, **loader_options)
test_loader = DataLoader(test_dataset, shuffle=False, **loader_options)

print("DATASET LOADED SUCCESSFULLY")
print("Dataset:", DATA_DIR)
print("Classes:", num_classes)
print("Training Images:", len(train_dataset))
print("Validation Images:", len(val_dataset))
print("Testing Images:", len(test_dataset))
print("Batch Size:", BATCH_SIZE, "Image Size:", IMG_SIZE, "Workers:", NUM_WORKERS)

if __name__ == "__main__":
    images, labels = next(iter(train_loader))
    print("Batch test:", tuple(images.shape), tuple(labels.shape))
