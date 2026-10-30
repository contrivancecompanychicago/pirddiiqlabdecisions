# pirddiiqlab

This repository contains code and experiments for the pirddiiqlab project: a Python health-data and insights platform for human families.

## Current status

The repository includes an early Flask backend prototype and a growing set of local experiments. The backend remains suitable for local development and integration prototyping, but it is not a production clinical system or an approved medical workflow implementation.

## Project evolution and provenance

This repository was updated to integrate a small, fictionalized subset of ideas from the IMHOTEP Bizarros prototype repository:

- Source repo: `contrivancecompanychicago/imhotep-bizarro-secretary-backend`
- Purpose used here: a medical secretary / intake workflow reference, adapted into a minimal Flask app pattern
- Scope retained: fictional scheduling, intake prompts, secretary-style workflow categories, and notebook-friendly API experimentation
- Scope intentionally omitted: FastAPI stack, JWT auth, source research notebooks, real patient records, sensitive clinical data, and any claim of clinical validity or institutional approval

This keeps the target repo aligned with its existing architecture and conventions while adding a small intake-oriented layer for demonstration use.

## Backend: Version 0 (`pirddiiqlab-backend-v0`)

The current backend is a minimal Flask + SQLite service.

### Runtime implementations

- `app.py` — standalone Flask application and legacy v0 API.
- `pirddiiqlab/backend.py` — Flask application factory, SQLAlchemy models, and packaged API routes.
- `pirddiiqlab/cli.py` — command-line server launcher.
- `pirddiiqlab/init.py` — package metadata and `create_app` export.
- `pirddiiqlab/knowledge_base.py` — fictional intake knowledge-base reference adapted from the IMHOTEP prototype.
- `pirddiiqlab/colab.py` — helpers for running in Google Colab.
- `pirddiiqlab/openai_intake.py` — OpenAI-based fictional intake summarization for notebook demos.
- `notebooks/colab_demo.ipynb` — notebook example for launching the Flask app and calling the intake endpoint in Colab.

### Current database

The prototype uses SQLite by default:

- Default database: `pirddiiqlab_v0.db`
- Override with `PIRDDIIQLAB_DB_PATH`
- Existing tables:
  - `items` — generic key-value records
  - `updates` — received update payloads and timestamps

SQLite is appropriate for local development and demonstrations.

### Current endpoints

- `GET/POST /items` — list items or create/update an item by key.
- `GET/PUT/DELETE /items/<id>` — operate on an individual item.
- `POST /update` — receive update events and optionally apply `set` or `delete` operations.
- `GET /health` — return backend health and version information.
- `GET /api/v1/intake/knowledge-base` — return a fictional medical secretary intake knowledge base adapted from the IMHOTEP prototype.
- `POST /api/v1/intake/openai` — summarize a fictional intake payload using OpenAI when configured.
- `GET /init-db` — create missing prototype tables.

Example OpenAI intake payload:

```json
{
  "patient_name": "Sample Fictional Patient",
  "reason_for_visit": "New patient intake and scheduling needs",
  "appointment_type": "Follow-up visit",
  "preferred_contact": "Email",
  "insurance_status": "Fictional coverage pending review"
}
```

## OpenAI + Colab notebook workflow

This repository supports a minimal notebook-based intake demo. The goal is not to replace real clinical intake systems, but to demonstrate how a fictional secretary workflow could be built on top of this Flask app in a Colab environment.

### Colab setup

From a Google Colab notebook:

```python
!git clone https://github.com/contrivancecompanychicago/pirddiiqlabdecisions.git
%cd pirddiiqlabdecisions
!pip install -e .
!pip install openai
```

Then set the API key and start the app:

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-..."

from pirddiiqlab.colab import launch_colab_app

app = launch_colab_app()
app.run(host="0.0.0.0", port=8080)
```

### Example request

```python
import requests

response = requests.post(
    "http://127.0.0.1:8080/api/v1/intake/openai",
    json={
        "patient_name": "Sample Fictional Patient",
        "reason_for_visit": "New patient intake and scheduling needs",
        "appointment_type": "Follow-up visit",
        "preferred_contact": "Email",
        "insurance_status": "Fictional coverage pending review",
    },
)
print(response.json())
```

## Notebook example

The repository includes a notebook example at:

- `notebooks/colab_demo.ipynb`

This notebook shows how to:

- clone the repo in Colab
- install dependencies
- launch the local Flask app
- call the fictional intake API from the notebook

## Boundaries and safety notes

This project is intentionally limited to fictional, non-identifying intake and scheduling examples.

Do not use this repository to:

- store real patient records
- use real contact information
- claim clinical effectiveness or approval
- port raw research notebooks into production
- rely on the source prototype as a validated clinical workflow

The implementation is for local experimentation, prototype demos, and notebook-based workflows only.

## Running locally

Python 3.9 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The server listens on the `PORT` environment variable when set, or port `8080` by default.

The packaged CLI is intended to run as follows:

```bash
pip install -e .
pirddiiqlab-server --port 8080
```

## Development dependencies

The `pyproject.toml` file defines optional development dependencies for pytest, coverage, Black, Flake8, and mypy:

```bash
pip install -e ".[dev]"
```

## License

See the repository license file for licensing terms.
