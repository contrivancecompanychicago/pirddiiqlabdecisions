"""Device-neutral CGM readings API for local, synthetic-data demonstrations.

This prototype is not a medical device and must not be used with real patient data.
"""

from __future__ import annotations

import math
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from typing import Any

from flask import Flask, jsonify, request

MAX_BATCH_SIZE = 500
MAX_READINGS_PER_QUERY = 5000


def _connect(database_path: str) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def _initialize_database(database_path: str) -> None:
    if database_path != ":memory:":
        parent = os.path.dirname(os.path.abspath(database_path))
        os.makedirs(parent, exist_ok=True)
    with _connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cgm_readings (
                reading_id TEXT PRIMARY KEY,
                participant_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                glucose_mg_dl REAL NOT NULL,
                source TEXT NOT NULL
            )
            """
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS ix_cgm_participant_timestamp "
            "ON cgm_readings (participant_id, timestamp)"
        )


def _parse_timestamp(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("timestamp must be an ISO 8601 string with a timezone")
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be a valid ISO 8601 string") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("timestamp must include a timezone, such as Z or -05:00")
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _validate_reading(reading: Any) -> dict[str, Any]:
    if not isinstance(reading, dict):
        raise ValueError("each reading must be a JSON object")

    participant_id = reading.get("participant_id")
    if not isinstance(participant_id, str) or not participant_id.strip():
        raise ValueError("participant_id is required")
    participant_id = participant_id.strip()
    if len(participant_id) > 80:
        raise ValueError("participant_id must be at most 80 characters")

    value = reading.get("glucose_mg_dl")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("glucose_mg_dl must be a number")
    glucose = float(value)
    # Broad input sanity bounds only; they are not clinical thresholds or alerts.
    if not math.isfinite(glucose) or glucose < 20 or glucose > 600:
        raise ValueError("glucose_mg_dl must be between 20 and 600 for this demo API")

    source = reading.get("source", "synthetic-demo")
    if not isinstance(source, str) or not source.strip() or len(source) > 80:
        raise ValueError("source must be a non-empty string of at most 80 characters")

    return {
        "reading_id": str(uuid.uuid4()),
        "participant_id": participant_id,
        "timestamp": _parse_timestamp(reading.get("timestamp")),
        "glucose_mg_dl": glucose,
        "source": source.strip(),
    }


def create_app(database_path: str | None = None) -> Flask:
    """Create the standalone CGM demo API backed by a local SQLite database."""
    app = Flask(__name__)
    database_path = database_path or os.environ.get(
        "PIRDDIIQLAB_CGM_DB_PATH", "/tmp/pirddiiqlab_cgm_demo.sqlite3"
    )
    app.config["CGM_DATABASE_PATH"] = database_path
    _initialize_database(database_path)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "synthetic-cgm-demo-api"})

    @app.post("/api/v1/cgm/readings")
    def create_readings():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "request body must be a JSON object"}), 400

        raw_readings = payload.get("readings")
        if not isinstance(raw_readings, list) or not raw_readings:
            return jsonify({"error": "readings must be a non-empty array"}), 400
        if len(raw_readings) > MAX_BATCH_SIZE:
            return jsonify({"error": f"at most {MAX_BATCH_SIZE} readings may be submitted at once"}), 400

        try:
            readings = [_validate_reading(item) for item in raw_readings]
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        with _connect(app.config["CGM_DATABASE_PATH"]) as connection:
            connection.executemany(
                """INSERT INTO cgm_readings
                   (reading_id, participant_id, timestamp, glucose_mg_dl, source)
                   VALUES (:reading_id, :participant_id, :timestamp, :glucose_mg_dl, :source)""",
                readings,
            )

        return jsonify({"status": "accepted", "count": len(readings), "readings": readings}), 201

    @app.get("/api/v1/cgm/readings")
    def list_readings():
        participant_id = request.args.get("participant_id", "").strip()
        if not participant_id:
            return jsonify({"error": "participant_id query parameter is required"}), 400
        if len(participant_id) > 80:
            return jsonify({"error": "participant_id must be at most 80 characters"}), 400

        raw_limit = request.args.get("limit", "500")
        try:
            limit = int(raw_limit)
        except ValueError:
            return jsonify({"error": "limit must be an integer"}), 400
        if limit < 1 or limit > MAX_READINGS_PER_QUERY:
            return jsonify({"error": f"limit must be between 1 and {MAX_READINGS_PER_QUERY}"}), 400

        with _connect(app.config["CGM_DATABASE_PATH"]) as connection:
            rows = connection.execute(
                """SELECT reading_id, participant_id, timestamp, glucose_mg_dl, source
                   FROM cgm_readings WHERE participant_id = ?
                   ORDER BY timestamp DESC, reading_id DESC LIMIT ?""",
                (participant_id, limit),
            ).fetchall()
        return jsonify({"participant_id": participant_id, "count": len(rows), "readings": [dict(r) for r in rows]})

    return app


if __name__ == "__main__":
    demo_app = create_app()
    # Loopback only: do not expose this unauthenticated demo service to a network.
    demo_app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
