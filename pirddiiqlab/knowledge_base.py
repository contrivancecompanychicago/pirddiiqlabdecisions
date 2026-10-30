"""Minimal knowledge-base support for fictional medical secretary intake workflows.

This module intentionally adapts only a small subset of the IMHOTEP Bizarros
prototype concepts. It does not carry over the source project's research,
clinical claims, or private data handling assumptions.
"""

from typing import Any, Dict

SOURCE_REPO = "contrivancecompanychicago/imhotep-bizarro-secretary-backend"

FICTIONAL_INTAKE_KB = {
    "appointment_scheduling": {
        "title": "Appointment scheduling",
        "description": "Fictional scheduling tasks for intake coordination.",
        "items": [
            "Confirm preferred visit type and time window.",
            "Capture fictional availability, contact preference, and reminder timing.",
            "Track follow-up tasks without using real patient record data.",
        ],
    },
    "insurance_verification": {
        "title": "Insurance verification",
        "description": "Synthetic payer and coverage verification tasks for demonstration use only.",
        "items": [
            "Review fictional payer information and status notes.",
            "Record eligibility or referral notes in test data only.",
            "Keep verification workflow separate from clinical decision-making.",
        ],
    },
    "intake_questionnaire": {
        "title": "Intake questionnaire",
        "description": "Structured secretary-facing prompts for fictional patient intake.",
        "items": [
            "Collect preferred language, referral source, and reason for visit.",
            "Document practice contact preferences and scheduling constraints.",
            "Store only synthetic or test-case data.",
        ],
    },
    "care_coordination": {
        "title": "Care coordination",
        "description": "Follow-up and coordination tasks framed as operational workflow support.",
        "items": [
            "Prepare reminder tasks for follow-up outreach.",
            "Track communication notes in a fictional workflow context.",
            "Keep all tasks separated from real-world medical decisions.",
        ],
    },
}


def get_intake_knowledge_base() -> Dict[str, Any]:
    """Return the adapted fictional knowledge-base payload."""
    return {
        "source_repo": SOURCE_REPO,
        "source_note": "Adapted from the IMHOTEP Bizarros prototype for a fictional medical secretary intake workflow reference.",
        "fictional_data_only": True,
        "categories": list(FICTIONAL_INTAKE_KB.keys()),
        "items": FICTIONAL_INTAKE_KB,
    }
