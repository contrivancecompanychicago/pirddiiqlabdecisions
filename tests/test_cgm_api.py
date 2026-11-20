import pytest

from pirddiiqlab.cgm_api import create_app


@pytest.fixture
 def_client_path():
    """Use a fresh on-disk database per test."""
    import tempfile

    with tempfile.TemporaryDirectory() as directory:
        yield f"{directory}/cgm.sqlite3"


@pytest.fixture
 def_client(def_client_path):
    app = create_app(def_client_path)
    app.config["TESTING"] = True
    return app.test_client()


def valid_reading(**changes):
    reading = {
        "participant_id": "synthetic-001",
        "timestamp": "2026-01-15T12:00:00Z",
        "glucose_mg_dl": 121.5,
        "source": "synthetic-test",
    }
    reading.update(changes)
    return reading


def test_post_and_get_synthetic_readings(def_client):
    response = def_client.post(
        "/api/v1/cgm/readings", json={"readings": [valid_reading()]}
    )
    assert response.status_code == 201
    assert response.get_json()["count"] == 1

    response = def_client.get(
        "/api/v1/cgm/readings?participant_id=synthetic-001"
    )
    payload = response.get_json()
    assert response.status_code == 200
    assert payload["count"] == 1
    assert payload["readings"][0]["glucose_mg_dl"] == 121.5


def test_invalid_batch_is_rejected_without_partial_insert(def_client):
    response = def_client.post(
        "/api/v1/cgm/readings",
        json={"readings": [valid_reading(), valid_reading(timestamp="not-a-date")]},
    )
    assert response.status_code == 400

    stored = def_client.get(
        "/api/v1/cgm/readings?participant_id=synthetic-001"
    ).get_json()
    assert stored["count"] == 0


def test_timestamp_must_include_timezone(def_client):
    response = def_client.post(
        "/api/v1/cgm/readings",
        json={"readings": [valid_reading(timestamp="2026-01-15T12:00:00")]},
    )
    assert response.status_code == 400
    assert "timezone" in response.get_json()["error"]


def test_readings_query_requires_participant_id(def_client):
    response = def_client.get("/api/v1/cgm/readings")
    assert response.status_code == 400
    assert "participant_id" in response.get_json()["error"]


def test_non_finite_and_boolean_glucose_values_are_rejected(def_client):
    for value in (float("nan"), True):
        response = def_client.post(
            "/api/v1/cgm/readings", json={"readings": [valid_reading(glucose_mg_dl=value)]}
        )
        assert response.status_code == 400
