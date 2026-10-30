from __future__ import annotations

import json
import re
from typing import Any


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().lower().replace(",", "")
        if not cleaned:
            return None
        match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
        if match:
            return float(match.group(0))
    return None


def _stringify(value: Any) -> str:
    return json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value or "")


def _score_from_text(text: str) -> int:
    lowered = text.lower()
    score = 0
    scoring_map = {
        "critical": 25,
        "urgent": 18,
        "high": 15,
        "severe": 18,
        "risk": 12,
        "warning": 12,
        "alert": 15,
        "imhotep": 8,
        "approval": -10,
        "safe": -12,
        "normal": -8,
        "stable": -10,
        "low": -8,
        "ok": -5,
    }
    for phrase, weight in scoring_map.items():
        if phrase in lowered:
            score += weight
    return score


def build_decision_from_payload(source: str | None, payload: Any) -> dict[str, Any]:
    """Create a deterministic AI-style decision from incoming IMHOTEP or other data.

    This is intentionally rule-based and deterministic so the application can work without an
    external LLM dependency while still producing a structured decision payload for incoming data.
    """
    data = payload if isinstance(payload, dict) else {"value": payload}
    source_name = (source or "unknown").strip().lower()
    text_blob = _stringify(data).lower()

    if source_name == "imhotep" or "imhotep" in text_blob:
        source_name = "imhotep"

    risk_score = 0
    for key in [
        "risk",
        "risk_score",
        "severity",
        "severity_score",
        "priority",
        "criticality",
        "urgency",
        "confidence",
        "impact",
    ]:
        if key in data:
            risk_score += max(0, min(40, int(round(_as_float(data.get(key)) or 0) * 1.5)))

    for status in ["critical", "urgent", "high", "warning", "alert", "escalate", "fraud", "anomaly"]:
        if status in text_blob:
            risk_score += 12

    risk_score += _score_from_text(text_blob)

    if "approved" in text_blob or "clear" in text_blob or "stable" in text_blob:
        risk_score -= 15

    risk_score = max(0, min(100, risk_score))

    if risk_score < 25:
        decision = "approve"
        recommended_action = "continue"
    elif risk_score < 50:
        decision = "review"
        recommended_action = "route_to_human_review"
    elif risk_score < 75:
        decision = "escalate"
        recommended_action = "notify_operators"
    else:
        decision = "halt"
        recommended_action = "lock_and_investigate"

    confidence = max(0.45, min(0.95, 0.5 + (100 - risk_score) / 200 + (0.1 if source_name == "imhotep" else 0)))
    confidence = round(confidence, 3)

    return {
        "source": source_name,
        "decision": decision,
        "risk_score": risk_score,
        "confidence": confidence,
        "recommended_action": recommended_action,
        "reason": (
            "IMHOTEP signal indicates a clear operational decision based on priority, severity, "
            "and confidence thresholds."
            if source_name == "imhotep"
            else "Structured scoring classified the incoming payload for operational review."
        ),
        "input_summary": text_blob[:500],
    }
