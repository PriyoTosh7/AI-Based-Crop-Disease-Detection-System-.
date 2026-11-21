
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs"
EVAL = OUTPUT / "evaluation"

EVAL.mkdir(parents=True, exist_ok=True)

# Find existing confusion matrix
candidates = [
    OUTPUT / "confusion_matrix.npy",
    EVAL / "confusion_matrix.npy"
]

matrix_path = next(
    (p for p in candidates if p.exists()),
    None
)

if matrix_path is None:
    raise FileNotFoundError(
        "confusion_matrix.npy not found in outputs"
    )

# Load class names from report
report_path = EVAL / "class_wise_report.csv"

if not report_path.exists():
    raise FileNotFoundError(report_path)

df = pd.read_csv(report_path, index_col=0)

class_names = [
    name for name in df.index
    if name not in ["accuracy", "macro avg", "weighted avg"]
]

cm = np.load(matrix_path)

if cm.shape != (len(class_names), len(class_names)):
    raise ValueError(
        f"Matrix shape {cm.shape} does not match "
        f"{len(class_names)} classes"
    )

print("Confusion Matrix Loaded:", cm.shape)

# ==========================================
# TOP CONFUSED CLASS PAIRS
# ==========================================

errors = []

for actual in range(len(class_names)):
    for predicted in range(len(class_names)):

        if actual != predicted and cm[actual, predicted] > 0:

            errors.append({
                "Actual Class": class_names[actual],
                "Predicted Class": class_names[predicted],
                "Misclassified Images": int(
                    cm[actual, predicted]
                )
            })

error_df = pd.DataFrame(errors)

if not error_df.empty:

    error_df = error_df.sort_values(
        "Misclassified Images",
        ascending=False
    )

    error_df.to_csv(
        EVAL / "confused_class_pairs.csv",
        index=False
    )

    print("\n===== TOP 20 CONFUSION PAIRS =====")
    print(error_df.head(20).to_string(index=False))

else:
    print("No classification errors found.")

# ==========================================
# PER-CLASS PERFORMANCE
# ==========================================

rows = []

for i, name in enumerate(class_names):

    total = int(cm[i].sum())
    correct = int(cm[i, i])
    incorrect = total - correct

    recall = correct / total * 100 if total else 0

    rows.append({
        "Class": name,
        "Correct": correct,
        "Incorrect": incorrect,
        "Total": total,
        "Recall (%)": round(recall, 4)
    })

class_df = pd.DataFrame(rows)

class_df = class_df.sort_values("Recall (%)")

class_df.to_csv(
    EVAL / "per_class_confusion_analysis.csv",
    index=False
)

print("\n===== LOWEST 10 CLASS RECALL =====")
print(class_df.head(10).to_string(index=False))

# ==========================================
# TOP CONFUSION VISUALIZATION
# ==========================================

if not error_df.empty:

    top = error_df.head(15).iloc[::-1]

    labels = [
        f"{row['Actual Class']} → {row['Predicted Class']}"
        for _, row in top.iterrows()
    ]

    plt.figure(figsize=(12, 9))

    plt.barh(
        labels,
        top["Misclassified Images"]
    )

    plt.xlabel("Number of Misclassified Images")
    plt.title("Top 15 Plant Disease Classification Errors")

    plt.tight_layout()

    plt.savefig(
        EVAL / "top_confusion_pairs.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

# ==========================================
# SUMMARY
# ==========================================

total_images = int(cm.sum())
correct_images = int(np.trace(cm))
wrong_images = total_images - correct_images

print("\n===== CONFUSION MATRIX SUMMARY =====")
print("Total Images:", total_images)
print("Correct Predictions:", correct_images)
print("Incorrect Predictions:", wrong_images)
print(
    "Matrix Accuracy:",
    round(correct_images / total_images * 100, 4),
    "%"
)

print("\nALL ANALYSIS COMPLETED!")
print("Output:", EVAL)
