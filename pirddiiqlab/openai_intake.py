"""OpenAI-powered fictional intake helpers for Colab use.

This module adds a lightweight intake summary flow suitable for a demo or
notebook environment. It intentionally uses fictional data only and does not
attempt clinical interpretation or real-patient handling.
"""

import json
import os
from typing import Any, Dict

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover
    OpenAI = None


def get_openai_api_key() -> str | None:
    """Read the API key from environment variables."""
    return os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY")


def build_intake_prompt(payload: Dict[str, Any]) -> str:
    """Build a secure prompt for fictional intake summarization."""
    normalized = payload or {}
    patient_name = normalized.get("patient_name") or "Sample fictional patient"
    reason_for_visit = normalized.get("reason_for_visit") or "routine intake"
    insurance_status = normalized.get("insurance_status") or "fictional status pending"
    appointment_type = normalized.get("appointment_type") or "initial consultation"
    preferred_contact = normalized.get("preferred_contact") or "email"

    return (
        "You are a fictional medical secretary intake assistant. "
        "Use only fictional, non-identifying data. "
        "Do not claim clinical validity, approvals, or patient-specific medical decisions. "
        "Return valid JSON only with keys: 'patient_name', 'reason_for_visit', 'appointment_type', "
        "'preferred_contact', 'insurance_status', 'summary', 'next_steps'.\n\n"
        f"patient_name: {patient_name}\n"
        f"reason_for_visit: {reason_for_visit}\n"
        f"appointment_type: {appointment_type}\n"
        f"preferred_contact: {preferred_contact}\n"
        f"insurance_status: {insurance_status}\n"
        "Also include a short fictional summary and next steps for a secretary workflow."
    )


def generate_intake_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a structured fictional intake summary using OpenAI when available."""
    if not payload:
        raise ValueError("Payload cannot be empty.")

    api_key = get_openai_api_key()
    if not api_key:
        return {
            "patient_name": payload.get("patient_name") or "Fictional patient",
            "reason_for_visit": payload.get("reason_for_visit") or "Routine intake",
            "appointment_type": payload.get("appointment_type") or "Initial intake",
            "preferred_contact": payload.get("preferred_contact") or "Email",
            "insurance_status": payload.get("insurance_status") or "Fictional status pending",
            "summary": "Fictional intake summary generated locally because no OpenAI API key was configured.",
            "next_steps": [
                "Confirm scheduling details with the fictional contact method.",
                "Validate coverage notes in a synthetic test workflow.",
                "Prepare a secretary-facing checklist before the visit.",
            ],
            "source": "local_fallback",
        }

    if OpenAI is None:
        raise RuntimeError("The openai package is not installed. Install it with pip install openai.")

    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    client = OpenAI(api_key=api_key)
    prompt = build_intake_prompt(payload)

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a fictional intake assistant for a medical secretary workflow. "
                    "Use only fictional, non-identifying data. Do not claim medical validity, "
                    "clinical approval, or connection to real patients."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    raw = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"summary": raw, "source": "openai_raw"}

    parsed.setdefault("source", "openai")
    return parsed
