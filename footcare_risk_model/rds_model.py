"""Load the published Fine-Gray RDS model directly in Python using rdata."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from .model import FootCareRiskModel, ModelArtifactError


def _get_field(value: Any, name: str) -> Any:
    if isinstance(value, Mapping) and name in value:
        return value[name]
    if hasattr(value, name):
        return getattr(value, name)
    raise ModelArtifactError(f"RDS model is missing expected field {name!r}")


def _named_coefficients(value: Any) -> tuple[list[str], np.ndarray]:
    if isinstance(value, pd.Series):
        names = [str(name) for name in value.index]
        numbers = value.to_numpy(dtype=float)
    elif isinstance(value, Mapping):
        names = [str(name) for name in value]
        numbers = np.asarray(list(value.values()), dtype=float)
    else:
        names_attr = getattr(value, "names", None)
        names = [str(name) for name in names_attr] if names_attr is not None else []
        numbers = np.asarray(value, dtype=float).reshape(-1)
    if not names or len(names) != len(numbers) or len(set(names)) != len(names):
        raise ModelArtifactError(
            "Python could not retain the named coefficient vector from the RDS. "
            "Use a compatible rdata release or export the model with the documented R script."
        )
    if not np.all(np.isfinite(numbers)):
        raise ModelArtifactError("RDS coefficients contain non-finite values")
    return names, numbers


def _numeric_vector(value: Any, field: str) -> np.ndarray:
    if isinstance(value, pd.Series):
        value = value.to_numpy()
    result = np.asarray(value, dtype=float).reshape(-1)
    if not len(result) or not np.all(np.isfinite(result)):
        raise ModelArtifactError(f"RDS field {field!r} is not a finite numeric vector")
    return result


def model_from_r_object(model_object: Any) -> FootCareRiskModel:
    """Create a predictor from the converted R list (also useful for tests)."""
    fit = _get_field(model_object, "crrFit")
    coefficients, beta = _named_coefficients(_get_field(fit, "coef"))
    event_times = _numeric_vector(_get_field(fit, "uftime"), "crrFit$uftime")
    increments = _numeric_vector(_get_field(fit, "bfitj"), "crrFit$bfitj")
    splines = _get_field(model_object, "splines")
    knots = {
        key: _numeric_vector(_get_field(splines, field), f"splines${field}").tolist()
        for key, field in (("age", "age_knots"), ("creatinine", "creatinine_knots"),
                           ("hba1c", "hba1c_knots"), ("albumin", "albumin_knots"))
    }

    if len(event_times) != len(increments):
        raise ModelArtifactError("RDS baseline time and increment vectors have different lengths")
    if np.any(np.diff(event_times) <= 0) or np.any(event_times < 0):
        raise ModelArtifactError("RDS baseline event times are not strictly increasing")
    if np.any(increments < -1e-12):
        raise ModelArtifactError("RDS baseline subhazard increments must be non-negative")
    if len(coefficients) != len(beta):
        raise ModelArtifactError("RDS coefficient names and values do not match")

    predictor = object.__new__(FootCareRiskModel)
    predictor.feature_names = coefficients
    predictor.coefficients = beta
    predictor.times = event_times
    predictor.baseline = np.cumsum(np.maximum(increments, 0.0))
    predictor.knots = knots
    return predictor


def load_rds_model(path: str | Path) -> FootCareRiskModel:
    """Read the upstream ``final_FGR_clean.rds`` without requiring R.

    Requires the pure-Python ``rdata`` package. Only the plain R list, numeric
    vectors, and spline knots used for prediction are consumed; unsupported
    RDS conversions fail with an actionable error instead of guessing.
    """
    try:
        import rdata
    except ImportError as exc:
        raise ModelArtifactError(
            "Direct RDS loading needs the Python 'rdata' package. Install it with "
            "python -m pip install rdata. No R installation is needed."
        ) from exc

    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"RDS model file not found: {source}")
    try:
        reader = getattr(rdata, "read_rds", None)
        if reader is not None:
            converted = reader(source)
        else:
            parsed = rdata.parser.parse_file(source)
            converted = rdata.conversion.convert(parsed)
    except Exception as exc:
        raise ModelArtifactError(
            "Could not decode this RDS model with rdata. The model was not modified; "
            "check the rdata version or use the documented JSON export as a fallback."
        ) from exc
    return model_from_r_object(converted)
