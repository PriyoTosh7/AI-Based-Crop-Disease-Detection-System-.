"""Rebuild final validation metrics from the supplied root confusion matrix."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "outputs"
EVAL = OUTPUT / "evaluation"
MATRIX_PATH = OUTPUT / "confusion_matrix.npy"
CLASS_PATH = OUTPUT / "model_export" / "class_names.json"

if not MATRIX_PATH.is_file() or not CLASS_PATH.is_file():
    raise FileNotFoundError("Need outputs/confusion_matrix.npy and outputs/model_export/class_names.json")

cm = np.load(MATRIX_PATH)
class_names = json.loads(CLASS_PATH.read_text(encoding="utf-8"))
if cm.shape != (len(class_names), len(class_names)):
    raise ValueError(f"Confusion matrix shape {cm.shape} does not match {len(class_names)} classes")

support = cm.sum(axis=1).astype(float)
predicted = cm.sum(axis=0).astype(float)
correct = np.diag(cm).astype(float)
precision = np.divide(correct, predicted, out=np.zeros_like(correct), where=predicted > 0)
recall = np.divide(correct, support, out=np.zeros_like(correct), where=support > 0)
f1 = np.divide(2 * precision * recall, precision + recall, out=np.zeros_like(correct), where=(precision + recall) > 0)
total = int(cm.sum())
accuracy = float(correct.sum() / total * 100) if total else 0.0
macro_p, macro_r, macro_f1 = float(precision.mean() * 100), float(recall.mean() * 100), float(f1.mean() * 100)
weighted_p = float(np.average(precision, weights=support) * 100)
weighted_r = float(np.average(recall, weights=support) * 100)
weighted_f1 = float(np.average(f1, weights=support) * 100)

rows = []
for i, name in enumerate(class_names):
    rows.append({"class": name, "precision": precision[i], "recall": recall[i], "f1-score": f1[i], "support": int(support[i])})
report = pd.DataFrame(rows).set_index("class")
report.loc["accuracy"] = {"precision": np.nan, "recall": accuracy / 100, "f1-score": np.nan, "support": total}
report.loc["macro avg"] = {"precision": precision.mean(), "recall": recall.mean(), "f1-score": f1.mean(), "support": total}
report.loc["weighted avg"] = {"precision": weighted_p / 100, "recall": weighted_r / 100, "f1-score": weighted_f1 / 100, "support": total}
EVAL.mkdir(parents=True, exist_ok=True)
report.to_csv(EVAL / "class_wise_report.csv")
report.loc[class_names].sort_values("recall").to_csv(EVAL / "error_analysis.csv")

bg_idx = next((i for i, name in enumerate(class_names) if name == "Background_without_leaves"), None)
background = {}
if bg_idx is not None:
    background_total = int(support[bg_idx])
    background_correct = int(correct[bg_idx])
    non_background_total = total - background_total
    false_background = int(predicted[bg_idx] - correct[bg_idx])
    background = {
        "False Background Predictions": false_background,
        "Non-Background Test Images": non_background_total,
        "False Background Rate (%)": round(false_background / non_background_total * 100, 4) if non_background_total else 0.0,
        "Actual Background Images": background_total,
        "Correct Background Predictions": background_correct,
        "Background Recall (%)": round(background_correct / background_total * 100, 4) if background_total else 0.0,
    }

results = {
    "Model": "EfficientNet-B3", "Total Classes": len(class_names), "Test Images": total,
    "Test Accuracy (%)": round(accuracy, 4), "Macro Precision (%)": round(macro_p, 4),
    "Macro Recall (%)": round(macro_r, 4), "Macro F1 Score (%)": round(macro_f1, 4),
    "Weighted Precision (%)": round(weighted_p, 4), "Weighted Recall (%)": round(weighted_r, 4),
    "Weighted F1 Score (%)": round(weighted_f1, 4), "Device": "recorded evaluation device: CUDA",
    "Background Analysis": background,
}
(EVAL / "evaluation_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

weakest = sorted(rows, key=lambda x: x["recall"])[:5]
summary = {
    "Model": "EfficientNet-B3", "Test Accuracy": round(accuracy, 4),
    "Macro Precision": round(macro_p, 4), "Macro Recall": round(macro_r, 4),
    "Macro F1": round(macro_f1, 4), "Total Classes Evaluated": len(class_names),
    "Lowest Class Recall (%)": round(min(recall) * 100, 4),
    "Weakest 5 Classes": {x["class"]: round(x["recall"] * 100, 4) for x in weakest},
    "Background Analysis": background,
}
(EVAL / "final_validation.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

pairs = []
for i, actual in enumerate(class_names):
    for j, predicted_name in enumerate(class_names):
        if i != j and cm[i, j] > 0:
            pairs.append({"Actual Class": actual, "Predicted Class": predicted_name, "Misclassified Images": int(cm[i, j])})
pairs_df = pd.DataFrame(pairs, columns=["Actual Class", "Predicted Class", "Misclassified Images"])
if not pairs_df.empty:
    pairs_df = pairs_df.sort_values("Misclassified Images", ascending=False)
pairs_df.to_csv(OUTPUT / "confused_class_pairs.csv", index=False)
pairs_df.to_csv(EVAL / "confused_class_pairs.csv", index=False)

per_class = pd.DataFrame([{
    "Class": name, "Correct": int(cm[i, i]), "Incorrect": int(support[i] - cm[i, i]),
    "Total": int(support[i]), "Recall (%)": round(float(recall[i] * 100), 4),
    "Precision (%)": round(float(precision[i] * 100), 4), "F1 (%)": round(float(f1[i] * 100), 4),
} for i, name in enumerate(class_names)]).sort_values("Recall (%)")
per_class.to_csv(EVAL / "per_class_confusion_analysis.csv", index=False)

# Rebuild confusion-matrix visuals from the same canonical matrix.
try:
    import matplotlib.pyplot as plt
    for target_path, normalized in [
        (OUTPUT / "confusion_matrix.png", False),
        (EVAL / "confusion_matrix.png", False),
        (OUTPUT / "normalized_confusion_matrix.png", True),
    ]:
        values = cm.astype(float)
        if normalized:
            row_totals = values.sum(axis=1, keepdims=True)
            values = np.divide(values, row_totals, out=np.zeros_like(values), where=row_totals > 0)
        fig, ax = plt.subplots(figsize=(20, 18))
        image = ax.imshow(values, interpolation="nearest", cmap="Blues", aspect="auto")
        ax.set_title("EfficientNet-B3 " + ("Normalized " if normalized else "") + "Confusion Matrix")
        ax.set_xlabel("Predicted class")
        ax.set_ylabel("Actual class")
        ax.set_xticks(np.arange(len(class_names)))
        ax.set_yticks(np.arange(len(class_names)))
        ax.set_xticklabels(class_names, rotation=90, fontsize=6)
        ax.set_yticklabels(class_names, fontsize=6)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
        fig.tight_layout()
        fig.savefig(target_path, dpi=180, bbox_inches="tight")
        plt.close(fig)
except ImportError:
    print("matplotlib unavailable; existing confusion-matrix images were left unchanged")

print("Canonical evaluation reports rebuilt from:", MATRIX_PATH)
print("Test images:", total, "Accuracy:", round(accuracy, 4), "%")
print("Macro P/R/F1:", round(macro_p, 4), round(macro_r, 4), round(macro_f1, 4))
print("Background:", background)
print("Potato Early/Late metrics:")
for name in ("Potato___Early_blight", "Potato___Late_blight"):
    if name in report.index:
        print(name, report.loc[name].to_dict())
