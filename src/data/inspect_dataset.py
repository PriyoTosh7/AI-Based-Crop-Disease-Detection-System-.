"""Inspect a raw class-folder PlantVillage dataset from common project locations."""
import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]
EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


def class_root(path: Path) -> bool:
    return path.is_dir() and sum(p.is_dir() for p in path.iterdir()) >= 2

candidates = []
if os.getenv("PV_DATASET_DIR"):
    candidates.append(Path(os.environ["PV_DATASET_DIR"]).expanduser())
candidates += [
    PROJECT_DIR / "Plant_leave_diseases_dataset_with_augmentation",
    PROJECT_DIR / "dataset" / "raw" / "Plant_leave_diseases_dataset_with_augmentation",
    PROJECT_DIR / "dataset" / "raw",
]
DATASET_DIR = next((p.resolve() for p in candidates if class_root(p)), None)
if DATASET_DIR is None:
    raise FileNotFoundError("Raw dataset not found. Set PV_DATASET_DIR or place the dataset folder in the project root.")

print("=" * 60)
print("PLANTVILLAGE DATASET INSPECTION")
print("Dataset Path:", DATASET_DIR)
class_counts = {}
for folder in sorted(p for p in DATASET_DIR.iterdir() if p.is_dir()):
    count = sum(1 for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS)
    class_counts[folder.name] = count
    print(f"{folder.name}: {count} images")
print("=" * 60)
print("Total Classes:", len(class_counts))
print("Total Images:", sum(class_counts.values()))
if class_counts:
    print("Largest Class:", max(class_counts, key=class_counts.get), max(class_counts.values()))
    print("Smallest Class:", min(class_counts, key=class_counts.get), min(class_counts.values()))
