from app import app
from pirddiiqlab.decision_engine import build_decision_from_payload


def test_build_decision_from_payload_approve_when_safe():
    result = build_decision_from_payload("imhotep", {
        "status": "stable",
        "risk": 5,
        "message": "Everything is normal and safe."
    })

    assert result["source"] == "imhotep"
    assert result["decision"] == "approve"
    assert result["recommended_action"] == "continue"
    assert result["risk_score"] < 25


def test_build_decision_from_payload_halt_for_critical_alert():
    result = build_decision_from_payload("imhotep", {
        "severity": "critical",
        "risk": 82,
        "message": "Fraud alert and emergency escalation required."
    })

    assert result["source"] == "imhotep"
    assert result["decision"] == "halt"
    assert result["recommended_action"] == "lock_and_investigate"
    assert result["risk_score"] >= 75


def test_update_route_evaluates_imhotep_payload():
    client = app.test_client()
    response = client.post(
        "/update",
        json={
            "source": "imhotep",
            "type": "set",
            "key": "decision-test",
            "value": "alert",
            "payload": {
                "severity": "critical",
                "risk": 90,
                "message": "Critical anomaly detected."
            }
        }
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["status"] == "received"
    assert payload["source"] == "imhotep"
    assert "decision" in payload
    assert payload["decision"]["source"] == "imhotep"
    assert payload["decision"]["decision"] in {"escalate", "halt"}


def test_imhotep_decision_route_returns_decision_object():
    client = app.test_client()
    response = client.post(
        "/imhotep/decision",
        json={
            "source": "imhotep",
            "payload": {
                "severity": "urgent",
                "risk": 60,
                "message": "High risk but recoverable; operator review required."
            }
        }
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["status"] == "ok"
    assert payload["source"] == "imhotep"
    assert payload["decision"]["decision"] in {"review", "escalate", "halt"}
    assert payload["decision"]["risk_score"] >= 25
