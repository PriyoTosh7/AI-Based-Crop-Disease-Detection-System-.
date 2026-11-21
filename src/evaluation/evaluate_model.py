
# ============================================================
# PLANTVILLAGE-AI
# 39-CLASS MODEL BATCH EVALUATION
# ============================================================

import json
import os
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support
)

# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parents[2]

_model_path = Path(os.getenv("PV_CHECKPOINT_PATH", str(PROJECT_DIR / "checkpoints" / "best_finetuned_efficientnet_b3.pth"))).expanduser()
MODEL_PATH = _model_path if _model_path.is_absolute() else (PROJECT_DIR / _model_path).resolve()
_test_dir = Path(os.getenv("PV_TEST_DIR", str(PROJECT_DIR / "dataset" / "processed" / "test"))).expanduser()
TEST_DIR = _test_dir if _test_dir.is_absolute() else (PROJECT_DIR / _test_dir).resolve()

OUTPUT_DIR = PROJECT_DIR / "outputs" / "evaluation"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

IMG_SIZE = 300
BATCH_SIZE = 32

DEVICE = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

# ============================================================
# IMAGE TRANSFORMATION
# ============================================================

test_transform = transforms.Compose([
    transforms.Resize(320),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

# ============================================================
# LOAD CHECKPOINT
# ============================================================

print("\nLoading EfficientNet-B3...")

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

checkpoint = torch.load(
    MODEL_PATH,
    map_location="cpu",
    weights_only=True
)

class_names = list(checkpoint["class_names"])
num_classes = len(class_names)
if checkpoint.get("num_classes") is not None and int(checkpoint["num_classes"]) != num_classes:
    raise ValueError("Checkpoint num_classes does not match class_names.")

model = models.efficientnet_b3(weights=None)

model.classifier[1] = nn.Linear(
    model.classifier[1].in_features,
    num_classes
)

model.load_state_dict(
    checkpoint["model_state_dict"],
    strict=True
)

model = model.to(DEVICE)
model.eval()

print("Model Loaded Successfully!")
print("Device:", DEVICE)
print("Classes:", num_classes)

# ============================================================
# LOAD TEST DATASET
# ============================================================

if not TEST_DIR.exists():
    raise FileNotFoundError(f"Test dataset not found: {TEST_DIR}")

test_dataset = datasets.ImageFolder(
    TEST_DIR,
    transform=test_transform
)

expected_mapping = {
    name: index
    for index, name in enumerate(class_names)
}

if test_dataset.class_to_idx != expected_mapping:
    raise ValueError(
        "CLASS MAPPING MISMATCH! "
        "Check checkpoint and test dataset."
    )

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=torch.cuda.is_available()
)

print("Test Images:", len(test_dataset))

# ============================================================
# BATCH PREDICTION
# ============================================================

all_labels = []
all_predictions = []

print("\nStarting Batch Evaluation...")

with torch.inference_mode():

    for batch_index, (images, labels) in enumerate(test_loader):

        images = images.to(DEVICE, non_blocking=True)

        outputs = model(images)

        predictions = torch.argmax(outputs, dim=1)

        all_predictions.extend(
            predictions.cpu().numpy()
        )

        all_labels.extend(
            labels.numpy()
        )

        print(
            f"\rProcessed: "
            f"{min((batch_index + 1) * BATCH_SIZE, len(test_dataset))}"
            f"/{len(test_dataset)}",
            end=""
        )

print("\nEvaluation Completed!")

y_true = np.array(all_labels)
y_pred = np.array(all_predictions)

# ============================================================
# OVERALL METRICS
# ============================================================

accuracy = accuracy_score(y_true, y_pred) * 100

precision, recall, f1, _ = (
    precision_recall_fscore_support(
        y_true,
        y_pred,
        average="macro",
        zero_division=0
    )
)

cm = confusion_matrix(
    y_true,
    y_pred,
    labels=list(range(num_classes))
)

# ============================================================
# BACKGROUND ERROR ANALYSIS
# ============================================================

background_indices = [
    i for i, name in enumerate(class_names)
    if "background_without_leaves" in name.lower()
]

background_metrics = {}

if background_indices:

    bg_idx = background_indices[0]

    non_background_mask = y_true != bg_idx

    false_background = int(
        np.sum(
            (y_true != bg_idx) & (y_pred == bg_idx)
        )
    )

    non_background_total = int(
        np.sum(non_background_mask)
    )

    false_background_rate = (
        false_background / non_background_total * 100
        if non_background_total else 0.0
    )

    actual_background = int(
        np.sum(y_true == bg_idx)
    )

    correctly_detected_background = int(
        np.sum(
            (y_true == bg_idx) & (y_pred == bg_idx)
        )
    )

    background_metrics = {
        "False Background Predictions": false_background,
        "Non-Background Test Images": non_background_total,
        "False Background Rate (%)": round(
            false_background_rate, 4
        ),
        "Actual Background Images": actual_background,
        "Correct Background Predictions": (
            correctly_detected_background
        )
    }

# ============================================================
# CLASS-WISE REPORT
# ============================================================

report = classification_report(
    y_true,
    y_pred,
    labels=list(range(num_classes)),
    target_names=class_names,
    output_dict=True,
    zero_division=0
)

report_df = pd.DataFrame(report).transpose()

report_df.to_csv(
    OUTPUT_DIR / "class_wise_report.csv"
)

# ============================================================
# CONFUSION MATRIX
# ============================================================

plt.figure(figsize=(22, 19))

plt.imshow(
    cm,
    interpolation="nearest",
    cmap="Blues"
)

plt.title(
    "PlantVillage-AI - EfficientNet-B3 Confusion Matrix"
)

plt.colorbar()

plt.xticks(
    range(num_classes),
    class_names,
    rotation=90,
    fontsize=7
)

plt.yticks(
    range(num_classes),
    class_names,
    fontsize=7
)

plt.xlabel("Predicted Class")
plt.ylabel("Actual Class")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "confusion_matrix.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ============================================================
# SAVE FINAL REPORT
# ============================================================

final_results = {
    "Model": "EfficientNet-B3",
    "Total Classes": num_classes,
    "Test Images": len(test_dataset),
    "Test Accuracy (%)": round(accuracy, 4),
    "Macro Precision (%)": round(precision * 100, 4),
    "Macro Recall (%)": round(recall * 100, 4),
    "Macro F1 Score (%)": round(f1 * 100, 4),
    "Device": str(DEVICE),
    "Background Analysis": background_metrics
}

with open(
    OUTPUT_DIR / "evaluation_results.json",
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        final_results,
        file,
        indent=4
    )

# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 55)
print("FINAL BATCH EVALUATION RESULTS")
print("=" * 55)

print("Test Images:", len(test_dataset))
print(f"Test Accuracy: {accuracy:.2f}%")
print(f"Macro Precision: {precision * 100:.2f}%")
print(f"Macro Recall: {recall * 100:.2f}%")
print(f"Macro F1 Score: {f1 * 100:.2f}%")

if background_metrics:

    print("\nBACKGROUND ANALYSIS")

    for key, value in background_metrics.items():
        print(f"{key}: {value}")

print("\nClass-wise Report Saved!")
print("Confusion Matrix Saved!")
print("Evaluation JSON Saved!")

print("\nOutput Directory:", OUTPUT_DIR)

print("\nBATCH EVALUATION COMPLETED SUCCESSFULLY!")
