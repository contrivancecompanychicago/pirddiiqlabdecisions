"""Python prediction utilities for an exported Fine-Gray model artifact.

The published RDS is intentionally not loaded in Python. Use the companion R
export script once to produce a JSON artifact, then this module performs all
preprocessing and predictions without requiring R.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

MODEL_FILENAME = "footcare_fgr_model.json"
PREDICTORS = (
    "age", "sex_f", "elective_adm", "homelessness", "peripheral_AD",
    "coronary_AD", "stroke", "CHF", "hypertension", "COPD", "CKD",
    "malignancy", "mental_illness", "creatinine", "Hb_A1C", "albumin",
)
LABS = ("creatinine", "Hb_A1C", "albumin")
BINARY_PREDICTORS = PREDICTORS[1:13]


class ModelArtifactError(ValueError):
    """Raised when a model artifact is missing or inconsistent."""


def restricted_cubic_spline_basis(values: Sequence[float], knots: Sequence[float]) -> np.ndarray:
    """Return only the nonlinear columns from ``rms::rcs(..., norm=2)``.

    The original model separately includes each untransformed continuous
    predictor (for example ``age``) and adds the nonlinear columns as
    ``age1``, ``age2``, etc. This function therefore deliberately does not
    return the linear x column.
    """
    x = np.asarray(values, dtype=float)
    k = np.asarray(knots, dtype=float)
    if k.ndim != 1 or len(k) < 3 or not np.all(np.isfinite(k)):
        raise ValueError("knots must contain at least three finite values")
    if np.any(np.diff(k) <= 0):
        raise ValueError("knots must be strictly increasing")

    denominator = (k[-1] - k[0]) ** 2
    columns = []
    for j in range(len(k) - 2):
        first = np.maximum(x - k[j], 0.0) ** 3
        penultimate = np.maximum(x - k[-2], 0.0) ** 3
        last = np.maximum(x - k[-1], 0.0) ** 3
        term = (
            first
            - penultimate * (k[-1] - k[j]) / (k[-1] - k[-2])
            + last * (k[-2] - k[j]) / (k[-1] - k[-2])
        ) / denominator
        columns.append(term)
    return np.column_stack(columns)


def _numeric_column(frame: pd.DataFrame, name: str, *, allow_missing: bool = False) -> np.ndarray:
    if name not in frame:
        raise ValueError(f"Missing required predictor column: {name}")
    try:
        values = pd.to_numeric(frame[name], errors="raise").to_numpy(dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Predictor {name!r} must contain numeric values") from exc
    invalid = ~np.isfinite(values)
    if allow_missing:
        invalid &= ~np.isnan(values)
    if invalid.any():
        raise ValueError(f"Predictor {name!r} contains infinite or invalid values")
    return values


def _prepare_features(data: pd.DataFrame, artifact: Mapping[str, Any]) -> dict[str, np.ndarray]:
    if not isinstance(data, pd.DataFrame) or data.empty:
        raise ValueError("data must be a non-empty pandas DataFrame")
    features: dict[str, np.ndarray] = {}

    for name in PREDICTORS:
        is_lab = name in LABS
        values = _numeric_column(data, name, allow_missing=is_lab)
        if is_lab:
            missing_name = f"{name}_missing"
            missing = np.isnan(values)
            if missing_name in data:
                supplied = _numeric_column(data, missing_name)
                if np.any((supplied != 0) & (supplied != 1)):
                    raise ValueError(f"{missing_name} must contain only 0/1 values")
                missing |= supplied.astype(bool)
            features[missing_name] = missing.astype(float)
            values = np.where(missing, 0.0, values)
        elif name == "age" and np.isnan(values).any():
            raise ValueError("age cannot be missing")
        if name in BINARY_PREDICTORS:
            if np.isnan(values).any() or np.any((values != 0) & (values != 1)):
                raise ValueError(f"{name} must contain only 0/1 values")
        features[name] = values

    for variable, knot_key in (("age", "age"), ("creatinine", "creatinine"),
                               ("Hb_A1C", "hba1c"), ("albumin", "albumin")):
        if knot_key not in artifact["knots"]:
            raise ModelArtifactError(f"Artifact is missing knots for {knot_key}")
        basis = restricted_cubic_spline_basis(features[variable], artifact["knots"][knot_key])
        for index in range(basis.shape[1]):
            features[f"{variable}{index + 1}"] = basis[:, index]

    return features


def _feature_values(name: str, features: Mapping[str, np.ndarray]) -> np.ndarray:
    """Resolve ordinary terms and R's logical TRUE/FALSE dummy names."""
    if name in features:
        return features[name]
    for suffix, value in (("TRUE", 1.0), ("FALSE", 0.0)):
        if name.endswith(suffix):
            raw_name = name[:-len(suffix)]
            if raw_name in features:
                raw = features[raw_name]
                return raw if value == 1.0 else 1.0 - raw
    raise ModelArtifactError(f"No input feature can be mapped to coefficient {name!r}")


class FootCareRiskModel:
    """Predict cumulative incidence of foot complications from an exported model.

    The JSON artifact is generated from the repository's validated R model by
    ``export_model.R``. Time values and predictions are in days and probability
    units, respectively.
    """

    def __init__(self, model_path: str | Path | None = None):
        path = Path(model_path) if model_path else Path(__file__).with_name(MODEL_FILENAME)
        try:
            with path.open(encoding="utf-8") as source:
                artifact = json.load(source)
        except FileNotFoundError as exc:
            raise ModelArtifactError(
                f"Model artifact not found at {path}. See footcare_risk_model/README.md "
                "to export it from the original RDS model."
            ) from exc
        except json.JSONDecodeError as exc:
            raise ModelArtifactError(f"Invalid JSON model artifact: {path}") from exc

        try:
            names = artifact["feature_names"]
            coefficients = np.asarray(artifact["coefficients"], dtype=float)
            times = np.asarray(artifact["baseline_times_days"], dtype=float)
            baseline = np.asarray(artifact["baseline_cumulative_subhazard"], dtype=float)
            knots = artifact["knots"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ModelArtifactError("Artifact does not match the documented JSON schema") from exc
        if (not isinstance(names, list) or not names or len(set(names)) != len(names)
                or coefficients.shape != (len(names),)):
            raise ModelArtifactError("feature_names and coefficients must have matching lengths")
        if (times.ndim != 1 or baseline.shape != times.shape or len(times) < 2
                or not np.all(np.isfinite(times)) or not np.all(np.isfinite(baseline))
                or np.any(np.diff(times) <= 0) or np.any(np.diff(baseline) < -1e-12)
                or times[0] < 0 or np.any(baseline < 0)):
            raise ModelArtifactError("Baseline times and cumulative subhazards are invalid")
        if not np.all(np.isfinite(coefficients)):
            raise ModelArtifactError("coefficients must be finite")
        if not isinstance(knots, dict):
            raise ModelArtifactError("knots must be a JSON object")
        self.feature_names = names
        self.coefficients = coefficients
        self.times = times
        self.baseline = baseline
        self.knots = knots

    def predict(self, data: pd.DataFrame, times_days: float | Sequence[float] = 365.25) -> np.ndarray:
        """Return rows-by-times cumulative foot-complication risk estimates."""
        requested = np.atleast_1d(np.asarray(times_days, dtype=float))
        if requested.ndim != 1 or not len(requested) or not np.all(np.isfinite(requested)):
            raise ValueError("times_days must be a finite number or one-dimensional sequence")
        if np.any(requested < 0):
            raise ValueError("times_days cannot be negative")
        if np.any(requested > self.times[-1]):
            raise ValueError(f"Requested time exceeds artifact horizon ({self.times[-1]:g} days)")

        features = _prepare_features(data, {"knots": self.knots})
        design = np.column_stack([_feature_values(name, features) for name in self.feature_names])
        linear_predictor = design @ self.coefficients
        positions = np.searchsorted(self.times, requested, side="right") - 1
        h0 = np.where(positions < 0, 0.0, self.baseline[np.maximum(positions, 0)])
        cumulative_hazard = np.exp(np.clip(linear_predictor, -700, 700))[:, None] * h0[None, :]
        risks = -np.expm1(-cumulative_hazard)
        return risks[:, 0] if np.ndim(times_days) == 0 else risks


def predict_risk(data: pd.DataFrame, times_days: float | Sequence[float] = 365.25,
                 model_path: str | Path | None = None) -> np.ndarray:
    """Convenience wrapper returning risk probabilities for one or more times."""
    return FootCareRiskModel(model_path).predict(data, times_days)
