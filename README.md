# pirddiiqlab

This repository contains code and experiments for the pirddiiqlab project: a Python health-data and insights platform for human families.

## Package status

The project is now structured as an installable Python package. The package entry point is `pirddiiqlab`, with package metadata exposed via `pirddiiqlab/__init__.py` and version `0.1.0`.

The package is intended to be installed from the repository root with:

```bash
python -m pip install -e .
```

This installs the packaged backend and the CLI entry points for the project, including:

- `pirddiiqlab-server`
- `pirddiiq-footcare-risk`
- `pirddiiq-footcare-risk-rds`

The project metadata and distribution configuration are defined in `pyproject.toml`, and the source distribution includes both the backend package and the standalone FootCare model package.

## Current status

The repository includes an early Flask backend prototype, a packaged Python module for the backend, and standalone health-data experiments. The backend is suitable for local development and integration prototyping, but it is not yet intended for production deployment without additional security, validation, and operational hardening.

The project has also evolved to include an operational decision layer for incoming IMHOTEP-style payloads. This gives the backend a deterministic, AI-inspired decision engine that can evaluate risk, triage events, and return structured recommendations without relying on an external LLM.

## IMHOTEP decision engine

The repository includes a rule-based decision engine in `pirddiiqlab/decision_engine.py`.

It evaluates incoming structured data and produces a normalized decision object containing:

- `source`
- `decision`
- `risk_score`
- `confidence`
- `recommended_action`
- `reason`
- `input_summary`

The decision logic intentionally does not depend on an external LLM. Instead, it uses deterministic scoring from key fields such as:

- `risk`
- `risk_score`
- `severity`
- `severity_score`
- `priority`
- `criticality`
- `urgency`
- `confidence`
- `impact`

It also interprets text severity markers such as `critical`, `urgent`, `warning`, `alert`, `fraud`, and `anomaly` to classify payloads.

### Supported decisions

The engine returns one of the following:

- `approve`
- `review`
- `escalate`
- `halt`

The corresponding recommended actions are:

- `continue`
- `route_to_human_review`
- `notify_operators`
- `lock_and_investigate`

## API routes

The Flask application in `app.py` now includes:

- `GET /health` — returns backend health and version information.
- `GET/POST /items` — list or create/update key-value items.
- `GET/PUT/DELETE /items/<id>` — manage a specific item.
- `POST /update` — receives update events and optionally applies simple set/delete actions.
- `POST /imhotep/decision` — evaluates incoming IMHOTEP payloads and returns an AI-style operational decision.

### Example IMHOTEP decision request

```json
{
  "source": "imhotep",
  "payload": {
    "severity": "critical",
    "risk": 92,
    "message": "Fraud alert, emergency escalation required."
  }
}
```

### Example IMHOTEP decision response

```json
{
  "status": "ok",
  "source": "imhotep",
  "decision": {
    "source": "imhotep",
    "decision": "halt",
    "risk_score": 100,
    "confidence": 0.95,
    "recommended_action": "lock_and_investigate",
    "reason": "IMHOTEP signal indicates a clear operational decision based on priority, severity, and confidence thresholds.",
    "input_summary": "{\"severity\": \"critical\", \"risk\": 92, \"message\": \"Fraud alert, emergency escalation required.\"}"
  }
}
```

## Test coverage and validation

The repo includes a pytest suite covering:

- safe payload scoring
- critical payload risk classification
- `/update` integration for IMHOTEP payloads
- `/imhotep/decision` route behavior
- FootCare model preprocessing, risk calculations, and validation logic

This makes it straightforward to validate the scoring logic and endpoint behavior in CI or a local environment.

The team also used a Google Colab workflow to validate the logic in a notebook environment, with the same test suite invoked via:

```bash
!git clone https://github.com/contrivancecompanychicago/pirddiiqlabdecisions.git
%cd pirddiiqlabdecisions
!pip install -q -r requirements.txt
!pip install -q pytest
!pytest tests/test_imhotep_decision.py -q
```

## Backend: Version 0 (`pirddiiqlab-backend-v0`)

The current backend is a minimal Flask + SQLite service.

### Runtime implementations

- `app.py` — standalone Flask application and legacy v0 API.
- `pirddiiqlab/backend.py` — Flask application factory, SQLAlchemy models, and packaged API routes.
- `pirddiiqlab/cli.py` — command-line server launcher.
- `pirddiiqlab/__init__.py` — package metadata and import surface for installed usage.
- `pirddiiqlab/init.py` — legacy module retained for compatibility and package metadata.

The repository currently contains two similar backend entry points. They should be consolidated before production deployment so that the application, models, routes, and configuration have one single source of truth.

### Current database

The prototype uses SQLite by default:

- Default database: `pirddiiqlab_v0.db`
- Override with `PIRDDIIQLAB_DB_PATH`
- Existing tables:
  - `items` — generic key-value records
  - `updates` — received update payloads and timestamps

SQLite is appropriate for local development and demonstrations. A server-based database such as PostgreSQL is recommended for concurrent production use.

### Current endpoints

- `GET/POST /items` — list items or create/update an item by key.
- `GET/PUT/DELETE /items/<id>` — operate on an individual item.
- `POST /update` — receive update events and optionally apply `set` or `delete` operations.
- `GET /health` — return backend health and version information.
- `GET/POST /init-db` — create missing prototype tables.
- `POST /imhotep/decision` — evaluate incoming IMHOTEP payloads and return a structured decision.

Example item payload:

```json
{"key": "mykey", "value": "some value"}
```

Example update payload:

```json
{"source": "frontend", "type": "set", "key": "mykey", "value": "some value"}
```

## FootCare risk model package

The repository includes a separate installable package for the Diabetes Foot Complications Fine-Gray model at `footcare_risk_model/`.

This package is published as part of the overall `pirddiiqlab` project and exposes a Python API plus command-line access.

Install the package with:

```bash
python -m pip install -e .
```

Then use the package API or command-line tools:

```bash
pirddiiq-footcare-risk patients.csv scored_patients.csv --model footcare_risk_model/footcare_fgr_model.json --days 365.25 730.5
```

The package requires Python 3.9+, NumPy, and pandas. The optional RDS loader also supports `rdata` through the `rds` extra.

## Planned inventory and supply-chain architecture

The proposed inventory domain uses a normalized model:

```text
InventoryItem 1 ---- * InventoryLot 1 ---- * StockMovement
```

### Planned entities

- **`InventoryItem`** — catalog definition, including SKU, name, category, unit, reorder threshold, and active status.
- **`InventoryLot`** — a received batch, including lot number, quantity on hand, expiration date, storage location, and quarantine status.
- **`StockMovement`** — an inventory ledger entry for receipt, issue, transfer, disposal, or adjustment.

The intended relationship is:

- One inventory item can have many lots.
- One lot can have many stock movements.
- Stock movements should be append-only and auditable.
- Clients should not directly update `quantity_on_hand`; inventory changes should go through a transactional service operation.

### Planned API boundary

The future versioned API should use routes such as:

- `GET /api/v1/inventory`
- `POST /api/v1/inventory/receipts`
- `POST /api/v1/inventory/movements`
- `GET /api/v1/inventory/low-stock`
- `GET /api/v1/suppliers`
- `POST /api/v1/purchase-requests`
- `POST /api/v1/integrations/uic/events`
- `GET /health`

The UIC virtual lab should remain the user-facing system, while this service should become the source of truth for inventory and procurement records. Integration should use HTTPS, authenticated sessions, and explicit contract validation.

### Migration plan

The inventory models and migrations are an architecture plan and are not yet installed in the repository. The repository currently has no Flask-Migrate/Alembic migration directory.

The planned migration structure is:

```text
migrations/
  versions/
    <revision>_create_inventory_tables.py
pirddiiqlab/
  models/
    __init__.py
    inventory.py
```

The planned migration tooling is Flask-Migrate/Alembic. Production schema changes should be applied through migrations rather than `db.create_all()`.

Before implementing the inventory schema, the project should:

1. Add and register `InventoryItem`, `InventoryLot`, and `StockMovement` models.
2. Add Flask-Migrate and create the initial inventory migration.
3. Consolidate `app.py` and `pirddiiqlab/backend.py`.
4. Add service-layer transactions for receiving, issuing, transferring, and disposing stock.
5. Add authentication, authorization, validation, structured logging, and audit controls.
6. Add tests for migration upgrades, stock movements, insufficient stock, expiry, quarantine, and immutable movement history.
7. Move deployed environments from SQLite to PostgreSQL.

## Research and analysis scripts

The repository also contains standalone scripts and experiments, including:

- Cohort sampling with `Cohort.py`
- Chicago dietary analysis with `DartUPirddiiq.py`
- Diabetes emergency-visit analysis with `DiabetesEDVisits.py`
- BMI calculators in `bmi.py`, `bmi2.py`, and `bmi3.py`
- Food-label processing with `FoodLabel.py`
- Meal-planning experiments in `MealPrep*.py`
- Diabetes machine-learning experimentation with `MinoritiesDiabetesBaselineML.py`
- Synthetic persona generation with `SyntheticFacebook.py`
- Medication/adherence concepts in `SodiumButyrate*.py`

These scripts currently operate independently on local files or sample data. They are not part of the Flask request path and should remain isolated from supply-chain operations until their inputs and outputs are formalized.

## Security note

Do not place credentials, tokens, or other secrets in source control. Any credential previously committed in `Bard.py` should be considered compromised: revoke it, rotate it, and replace it with a safe secret-management approach.

## Running locally

Python 3.9 or newer is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,rds]'
python -m pirddiiqlab.cli --port 8080
```

The server listens on the `PORT` environment variable when set, or port `8080` by default.

The packaged CLI is intended to run as follows:

```bash
pip install -e .
pirddiiqlab-server --port 8080
```

The repo also supports direct model loading from upstream RDS files when the optional `rds` extra is installed.

## Development dependencies

The `pyproject.toml` file defines optional development dependencies for pytest, coverage, Black, Flake8, and mypy:

```bash
python -m pip install -e '.[dev,rds]'
```

This keeps the local development environment aligned with the project’s package setup and ensures the packaged CLI and model tooling can be exercised in test and CI contexts.

## License

See the repository license file for licensing terms.
