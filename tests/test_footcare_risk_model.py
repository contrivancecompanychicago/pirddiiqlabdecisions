import json

import numpy as np
import pandas as pd
import pytest

from footcare_risk_model import FootCareRiskModel, ModelArtifactError, restricted_cubic_spline_basis


def write_artifact(path):
    artifact = {
        "format_version": 1,
        "feature_names": ["age", "sex_f", "age1", "age2", "creatinine1", "creatinine2",
                          "Hb_A1C1", "Hb_A1C2", "albumin1"],
        "coefficients": [0.01, 0.2, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "knots": {"age": [40, 60, 80, 100], "creatinine": [40, 80, 120, 160],
                  "hba1c": [5, 7, 9, 12], "albumin": [20, 30, 40, 50]},
        "baseline_times_days": [0, 365.25, 730.5],
        "baseline_cumulative_subhazard": [0, 0.01, 0.02],
        "reference_linear_predictor": 0,
    }
    path.write_text(json.dumps(artifact), encoding="utf-8")


def patient(**changes):
    values = {
        "age": 67, "sex_f": 1, "elective_adm": 1, "homelessness": 0,
        "peripheral_AD": 0, "coronary_AD": 1, "stroke": 0, "CHF": 0,
        "hypertension": 1, "COPD": 0, "CKD": 0, "malignancy": 0,
        "mental_illness": 0, "creatinine": 140.0, "Hb_A1C": 8.5,
        "albumin": 32.1,
    }
    values.update(changes)
    return pd.DataFrame([values])


def test_rcs_basis_contains_only_nonlinear_columns():
    basis = restricted_cubic_spline_basis([40, 60, 80, 100], [40, 60, 80, 100])
    assert basis.shape == (4, 2)
    assert np.all(np.isfinite(basis))


def test_predict_returns_cumulative_risks_and_accepts_multiple_times(tmp_path):
    path = tmp_path / "model.json"
    write_artifact(path)
    model = FootCareRiskModel(path)
    one = model.predict(patient(), 365.25)
    both = model.predict(patient(), [365.25, 730.5])
    assert one.shape == (1,)
    assert both.shape == (1, 2)
    assert 0 < one[0] < both[0, 1] < 1


def test_missing_labs_are_zero_imputed_and_indicator_is_supported(tmp_path):
    path = tmp_path / "model.json"
    write_artifact(path)
    data = patient(Hb_A1C=np.nan)
    risk = FootCareRiskModel(path).predict(data, 365.25)
    assert np.isfinite(risk[0])


def test_predict_rejects_bad_binary_values_and_out_of_horizon(tmp_path):
    path = tmp_path / "model.json"
    write_artifact(path)
    model = FootCareRiskModel(path)
    with pytest.raises(ValueError, match="0/1"):
        model.predict(patient(sex_f=2), 365.25)
    with pytest.raises(ValueError, match="exceeds"):
        model.predict(patient(), 1000)


def test_missing_artifact_explains_conversion_step(tmp_path):
    with pytest.raises(ModelArtifactError, match="export it"):
        FootCareRiskModel(tmp_path / "absent.json")
