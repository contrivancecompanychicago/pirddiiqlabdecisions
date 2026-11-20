# CGM readings API demo in Google Colab

This standalone, device-neutral API demonstrates how to validate, store, and retrieve continuous glucose monitoring (CGM) readings using **synthetic data only**. It does not connect to a CGM device, provide clinical interpretation, or issue treatment guidance.

## Run in Colab

Open [`notebooks/cgm_readings_api_colab.ipynb`](../notebooks/cgm_readings_api_colab.ipynb) in Google Colab. The notebook clones this repository, installs the package, launches the API on loopback, submits the sample CSV, and retrieves readings for one synthetic participant.

## API contract

- `GET /health` — demo API health.
- `POST /api/v1/cgm/readings` — accepts `{"readings": [{"participant_id": "synthetic-001", "timestamp": "2026-01-15T08:00:00Z", "glucose_mg_dl": 104, "source": "synthetic-demo"}]}`. Batches are limited to 500 and validated atomically.
- `GET /api/v1/cgm/readings?participant_id=synthetic-001&limit=500` — retrieves readings only for the requested participant; `limit` is 1–5000.

Timestamps must be ISO 8601 and timezone-aware. Glucose must be a finite number from 20–600 mg/dL; this is a broad input sanity check, **not** a clinical range or alert threshold. Readings are normalized to UTC. SQLite storage is for local demonstration only.

## Local run and tests

```bash
python -m pip install -e .
python -m pirddiiqlab.cgm_api
python -m pytest tests/test_cgm_api.py -q
```

The local server binds to `127.0.0.1` and uses `/tmp/pirddiiqlab_cgm_demo.sqlite3` by default. Override the database with `PIRDDIIQLAB_CGM_DB_PATH`.

## Safety and privacy boundary

This is an unauthenticated prototype. **Never send real patient or device data to it or expose it to the internet.** The synthetic participant IDs do not represent people. Before any real pilot, the project needs security review, authentication and authorization, encryption, consent and data-retention policies, clinical oversight, validated device integration, and applicable privacy/regulatory review. The API does not diagnose, monitor emergencies, or recommend treatment. Patients should follow their care team's instructions and device labeling.
