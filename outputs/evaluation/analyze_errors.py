
import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[2]

REPORT = PROJECT_DIR / "outputs" / "evaluation" / "class_wise_report.csv"

df = pd.read_csv(REPORT, index_col=0)

df = df.loc[
    ~df.index.isin(["accuracy", "macro avg", "weighted avg"])
]

df = df.sort_values("recall", ascending=True)

print("\n===== BOTTOM 10 CLASSES =====\n")

print(
    df.head(10)[
        ["precision", "recall", "f1-score", "support"]
    ].to_string()
)

print("\n===== TOP 10 CLASSES =====\n")

print(
    df.tail(10).sort_values("recall", ascending=False)[
        ["precision", "recall", "f1-score", "support"]
    ].to_string()
)

output = PROJECT_DIR / "outputs" / "evaluation" / "error_analysis.csv"

df.to_csv(output)

print("\nError Analysis Saved:", output)
