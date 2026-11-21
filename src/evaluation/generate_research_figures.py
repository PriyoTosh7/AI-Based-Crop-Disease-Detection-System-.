
import json
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# ==========================================
# CONFIGURATION
# ==========================================

ROOT = Path(__file__).resolve().parents[2]
EVAL = ROOT / "outputs" / "evaluation"
FIGURES = ROOT / "outputs" / "research_figures"

FIGURES.mkdir(parents=True, exist_ok=True)

# ==========================================
# LOAD RESULTS
# ==========================================

with open(EVAL / "evaluation_results.json") as f:
    results = json.load(f)

df = pd.read_csv(
    EVAL / "class_wise_report.csv",
    index_col=0
)

df = df.drop(
    ["accuracy", "macro avg", "weighted avg"],
    errors="ignore"
)

# ==========================================
# FIGURE 1: OVERALL PERFORMANCE
# ==========================================

metrics = {
    "Accuracy": results["Test Accuracy (%)"],
    "Precision": results["Macro Precision (%)"],
    "Recall": results["Macro Recall (%)"],
    "F1-Score": results["Macro F1 Score (%)"]
}

plt.figure(figsize=(9, 6))

bars = plt.bar(
    metrics.keys(),
    metrics.values()
)

plt.ylim(90, 100)
plt.ylabel("Performance (%)")
plt.title("EfficientNet-B3 Overall Performance")

for bar, value in zip(bars, metrics.values()):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.1,
        f"{value:.2f}%",
        ha="center"
    )

plt.tight_layout()
plt.savefig(FIGURES / "overall_performance.png", dpi=300)
plt.close()

# ==========================================
# FIGURE 2: LOWEST 10 CLASS RECALL
# ==========================================

weakest = df.sort_values("recall").head(10)

plt.figure(figsize=(11, 7))

plt.barh(
    weakest.index,
    weakest["recall"] * 100
)

plt.xlabel("Recall (%)")
plt.title("10 Most Challenging Disease Classes")
plt.xlim(85, 100)

plt.tight_layout()
plt.savefig(FIGURES / "weakest_class_recall.png", dpi=300)
plt.close()

# ==========================================
# FIGURE 3: PRECISION VS RECALL
# ==========================================

plt.figure(figsize=(9, 7))

plt.scatter(
    df["precision"] * 100,
    df["recall"] * 100,
    alpha=0.8
)

plt.xlabel("Precision (%)")
plt.ylabel("Recall (%)")
plt.title("Class-wise Precision vs Recall")
plt.xlim(85, 101)
plt.ylim(85, 101)
plt.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(FIGURES / "precision_recall_plot.png", dpi=300)
plt.close()

# ==========================================
# FIGURE 4: BACKGROUND ANALYSIS
# ==========================================

bg = results.get("Background Analysis", {})

if bg:
    labels = [
        "Correct Background",
        "Missed Background",
        "False Background"
    ]

    values = [
        bg.get("Correct Background Predictions", 0),
        bg.get("Actual Background Images", 0)
        - bg.get("Correct Background Predictions", 0),
        bg.get("False Background Predictions", 0)
    ]

    plt.figure(figsize=(8, 5))

    plt.bar(labels, values)

    plt.ylabel("Number of Images")
    plt.title("Background Classification Analysis")

    plt.tight_layout()
    plt.savefig(
        FIGURES / "background_analysis.png",
        dpi=300
    )
    plt.close()

# ==========================================
# FINAL REPORT
# ==========================================

print("\nRESEARCH FIGURES GENERATED SUCCESSFULLY!")

for file in sorted(FIGURES.glob("*.png")):
    print(file.name)

print("\nOutput Directory:", FIGURES)
