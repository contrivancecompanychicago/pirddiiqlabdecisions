"""Command-line CSV predictor for the DFC Fine-Gray model."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .model import FootCareRiskModel


def main() -> int:
    parser = argparse.ArgumentParser(description="Predict diabetic foot-complication risk from CSV.")
    parser.add_argument("input_csv", type=Path, help="CSV containing model predictor columns")
    parser.add_argument("output_csv", type=Path, help="Destination CSV for predictions")
    parser.add_argument("--model", type=Path, help="Exported model JSON (defaults to packaged artifact)")
    parser.add_argument("--days", type=float, nargs="+", default=[365.25],
                        help="Prediction horizon(s) in days; default: 365.25")
    args = parser.parse_args()

    frame = pd.read_csv(args.input_csv)
    predictions = FootCareRiskModel(args.model).predict(frame, args.days)
    for index, days in enumerate(args.days):
        frame[f"foot_complication_risk_{days:g}_days"] = predictions[:, index]
    frame.to_csv(args.output_csv, index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
