import numpy as np
import pandas as pd
import pytest

from footcare_risk_model import ModelArtifactError
from footcare_risk_model.rds_model import model_from_r_object


def r_object():
    return {
        "crrFit": {
            "coef": pd.Series([0.01, 0.2], index=["age", "sex_fTRUE"]),
            "uftime": np.array([10.0, 365.25, 730.5]),
            "bfitj": np.array([0.001, 0.009, 0.01]),
        },
        "splines": {
            "age_knots": np.array([40, 60, 80, 100]),
            "creatinine_knots": np.array([40, 80, 120, 160]),
            "hba1c_knots": np.array([5, 7, 9, 12]),
            "albumin_knots": np.array([20, 30, 40]),
        },
    }


def patient():
    return pd.DataFrame([{
        "age": 67, "sex_f": 1, "elective_adm": 0, "homelessness": 0,
        "peripheral_AD": 0, "coronary_AD": 0, "stroke": 0, "CHF": 0,
        "hypertension": 0, "COPD": 0, "CKD": 0, "malignancy": 0,
        "mental_illness": 0, "creatinine": 80, "Hb_A1C": 7,
        "albumin": 30,
    }])


def test_model_from_converted_rds_object_predicts_risk():
    model = model_from_r_object(r_object())
    risk = model.predict(patient(), 365.25)
    assert risk.shape == (1,)
    assert 0 < risk[0] < 1
    assert np.isclose(model.baseline[-1], 0.02)


def test_model_from_rds_needs_named_coefficients():
    obj = r_object()
    obj["crrFit"]["coef"] = np.array([0.01, 0.2])
    with pytest.raises(ModelArtifactError, match="named coefficient"):
        model_from_r_object(obj)
