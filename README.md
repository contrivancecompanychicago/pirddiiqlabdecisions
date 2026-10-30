# pirddiiqlab

This repository contains code and experiments for the pirddiiqlab project: a Python health-data and insights platform for human families.

## Current status

The repository includes an early Flask backend prototype and a growing set of local experiments. The backend remains suitable for local development and integration prototyping, but it is not a production clinical system or an approved medical workflow implementation.

## Backend: Version 0 (`pirddiiqlab-backend-v0`)

The current backend is a minimal Flask + SQLite service.

### Runtime implementations

- `app.py` — standalone Flask application and legacy v0 API.
- `pirddiiqlab/backend.py` — Flask application factory, SQLAlchemy models, and packaged API routes.
- `pirddiiqlab/cli.py` — command-line server launcher.
- `pirddiiqlab/init.py` — package metadata and `create_app` export.
- `pirddiiqlab/knowledge_base.py` — fictional intake knowledge-base reference adapted from the IMHOTEP prototype.
- `pirddiiqlab/colab.py` — helpers for running in Google Colab.

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
- `GET /init-db` — create missing prototype tables.

Example item payload:

```json
{"key": "mykey", "value": "some value"}
```

Example update payload:

```json
{"source": "frontend", "type": "set", "key": "mykey", "value": "some value"}
```

## IMHOTEP integration note

This repository incorporates a small, adapted subset of concepts from the IMHOTEP Bizarros backend prototype for a fictional medical secretary / intake workflow reference.

Included:
- structured intake workflow categories
- fictional-only secretary-style task prompts
- knowledge-base documentation patterns with provenance notes

Intentionally not included:
- FastAPI app stack and JWT auth flow from the source repo
- raw research notebooks or experimental artifacts
- real patient records, private contact data, or sensitive clinical information
- claims of medical validity, institutional approval, or production clinical readiness

The source project is treated as a prototype/reference only and is adapted to fit the target repo's existing Flask architecture.

## Google Colab support

This repository is also configured to run in Google Colab with a minimal environment setup.

From a Colab notebook:

```python
!git clone https://github.com/contrivancecompanychicago/pirddiiqlabdecisions.git
%cd pirddiiqlabdecisions
!pip install -e .
```

Then start the app:

```python
from pirddiiqlab.backend import create_app
app = create_app()
app.run(host="0.0.0.0", port=8080)
```

The helper in `pirddiiqlab.colab` automatically sets the default SQLite path to `/content/pirddiiqlab_v0.db` when running in Colab.

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
