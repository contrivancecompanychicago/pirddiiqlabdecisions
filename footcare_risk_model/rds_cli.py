"""Run the official FootCare model directly from its RDS file using Python."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .rds_model import load_rds_model


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Score a CSV with the upstream Fine-Gray model RDS, using Python only."
    )
    parser.add_argument("input_csv", type=Path, help="CSV containing model predictor columns")
    parser.add_argument("output_csv", type=Path, help="Destination CSV for predictions")
    parser.add_argument("--model-rds", type=Path, required=True,
                        help="Path to upstream model/final_FGR_clean.rds")
    parser.add_argument("--days", type=float, nargs="+", default=[365.25],
                        help="Prediction horizon(s) in days; default: 365.25")
    args = parser.parse_args()

    model = load_rds_model(args.model_rds)
    patients = pd.read_csv(args.input_csv)
    risks = model.predict(patients, args.days)
    for index, days in enumerate(args.days):
        patients[f"foot_complication_risk_{days:g}_days"] = risks[:, index]
    patients.to_csv(args.output_csv, index=False)
    print(f"Scored {len(patients)} rows -> {args.output_csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
