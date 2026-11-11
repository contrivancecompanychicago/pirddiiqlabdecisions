# FootCare risk model — standalone Python package

This directory provides an installable Python interface to the Diabetes Foot
Complications Fine-Gray model in
[`PIRDDIIQ-FootCare-risk-model`](https://github.com/contrivancecompanychicago/PIRDDIIQ-FootCare-risk-model).
Once the model has been exported to JSON, prediction and CSV scoring run in
Python; R is not needed at runtime.

## Important: the trained model file is not bundled here

The validated coefficients, spline knots, and baseline subdistribution hazard
are stored in the upstream repository's RDS file. This repository does not
contain a converted model artifact, and the package intentionally does not
invent coefficients or approximate a clinical model. To create the JSON file,
run the included `export_model.R` once in the upstream repository using R and
its documented `riskRegression` / `rms` dependencies. Then copy the resulting
`footcare_fgr_model.json` into this directory. The R export is a one-time
conversion step; normal use is Python-only.

The exporter checks that coefficient names match the reconstructed model
matrix and stops rather than emitting a potentially misaligned model. Verify
the exported artifact against the upstream documented example (1-year risk
0.0171758 for its example patient) before using it. The package is not a
medical device and predictions are not a diagnosis or a substitute for
clinical judgment.

## Install

From the repository root:

```bash
python -m pip install -e .
```

This installs the `pirddiiq-footcare-risk` command and the package API. The
package requires Python 3.9+, NumPy, and pandas.

## Python example

Prepare one row per patient with the predictor names in
`PIRDDIIQ-FootCare-risk-model/data/data_dictionary.csv`. Binary columns accept
0/1 or booleans. Missing lab values are imputed to zero and receive the
corresponding missingness indicator automatically. You may instead provide
`creatinine_missing`, `Hb_A1C_missing`, and `albumin_missing` flags.

```python
import pandas as pd
from footcare_risk_model import FootCareRiskModel

patient = pd.DataFrame([{
    "age": 67, "sex_f": 1, "elective_adm": 1, "homelessness": 0,
    "peripheral_AD": 0, "coronary_AD": 1, "stroke": 0, "CHF": 0,
    "hypertension": 1, "COPD": 0, "CKD": 0, "malignancy": 0,
    "mental_illness": 0, "creatinine": 140.0, "Hb_A1C": 8.5,
    "albumin": 32.1,
}])

model = FootCareRiskModel("footcare_risk_model/footcare_fgr_model.json")
print(model.predict(patient, 365.25))  # risk probability at one year
print(model.predict(patient, [365.25, 2 * 365.25]))
```

## CSV command

```bash
pirddiiq-footcare-risk patients.csv scored_patients.csv --model footcare_risk_model/footcare_fgr_model.json --days 365.25 730.5
```

The input must contain all 16 predictor columns; missing laboratory values
may be blank. Output includes a risk-probability column for each requested
time horizon. Times are in days, and requested horizons must be within the
baseline curve horizon exported into the artifact.

## JSON artifact contract

The exporter creates `footcare_fgr_model.json` with these fields:

- `feature_names`: model-matrix column names, in coefficient order
- `coefficients`: Fine-Gray regression coefficients in that same order
- `knots`: restricted-cubic-spline knots for age, creatinine, HbA1c, albumin
- `baseline_times_days`: ascending time grid in days
- `baseline_cumulative_subhazard`: matching cumulative baseline subhazard
  values, relative to the reference linear predictor used during export
- `reference_linear_predictor`: reference predictor used by the exporter

Predictions use `1 - exp(-H0(t) * exp(linear_predictor))`, the Fine-Gray
cumulative-incidence form. Coefficients and baseline values must come from the
same fitted model and export; do not combine artifacts from different model
versions.

## Tests

```bash
python -m pytest tests/test_footcare_risk_model.py -q
```

Tests use an explicitly synthetic artifact and verify preprocessing, time
handling, spline construction, and validation; they do not represent clinical
validation of the original model.
