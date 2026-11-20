# pirddiiqlab

A Python health-data and insights platform for human families, with a focus on diabetes care research and equitable access for medically underserved communities in Chicago.

## Project purpose

PIRDDIIQ Lab is being developed to explore practical software support for people facing income barriers, limited access to care, housing instability, and other obstacles to diabetes management. A clinical continuous glucose monitoring (CGM) system must require qualified clinical oversight, validated integrations, privacy protections, regulatory review, and appropriate emergency workflows.

The repository is currently a mix of research experiments, Flask prototypes, and packaged health-risk utilities. Features should be treated as demonstrations unless they have undergone explicit clinical validation and production security review.

## Package status

The project is structured as an installable Python package. The package metadata is exposed through `pyproject.toml` and `pirddiiqlab/__init__.py`; the current package version is `0.1.0`.

Install for development:

```bash
python -m pip install -e '.[dev,rds]'
```

Package entry points include:

- `pirddiiqlab-server`
- `pirddiiq-footcare-risk`
- `pirddiiq-footcare-risk-rds`

The package author and maintainer information are:

- Eric Hilary Smith
- erichilarysmithsr@gmail.com

## Synthetic CGM readings prototype

The `feature/chicago-cgm-access` branch adds a first, synthetic-data-only CGM readings API.

Implementation:

- `pirddiiqlab/cgm_api.py` — device-neutral Flask API
- `data/synthetic_cgm_readings.csv` — 30 invented readings for synthetic participant IDs
- `tests/test_cgm_api.py` — API validation and storage tests
- `notebooks/cgm_readings_api_colab.ipynb` — Google Colab demonstration
- `docs/cgm_readings_api.md` — API and safety documentation

The API provides:

- `GET /health`
- `POST /api/v1/cgm/readings`
- `GET /api/v1/cgm/readings?participant_id=synthetic-001&limit=500`

Readings use timezone-aware ISO 8601 timestamps and are normalized to UTC. The API validates batch size and basic numeric sanity bounds. SQLite is used only for local demonstrations.

This prototype:

- Does not connect to a real CGM
- Does not use real or identifiable patient data
- Does not diagnose, monitor emergencies, or recommend treatment
- Is unauthenticated and must not be exposed to the internet
- Must not be used for clinical decisions

Before real-world use, the project requires authentication and authorization, encryption, consent and retention policies, clinical governance, validated device integrations, incident workflows, and applicable regulatory and privacy review.

## Run the synthetic CGM demo locally

Python 3.9 or newer is required.

```bash
python -m pip install -e '.[dev]'
python -m pirddiiqlab.cgm_api
python -m pytest tests/test_cgm_api.py -q
```

The demo server binds only to `127.0.0.1`. It uses `/tmp/pirddiiqlab_cgm_demo.sqlite3` by default; override this with `PIRDDIIQLAB_CGM_DB_PATH`.

## Google Colab CGM demo

Open `notebooks/cgm_readings_api_colab.ipynb` in Google Colab. The notebook:

1. Checks out `feature/chicago-cgm-access`
2. Installs the package
3. Starts the API locally in Colab
4. Loads synthetic readings from the repository CSV
5. Posts readings to the API
6. Retrieves readings for a synthetic participant
7. Runs validation and automated tests

Do not upload identifiable or confidential health data to a hosted notebook. The notebook is for synthetic demonstration only.

## Existing backend

The repository includes two Flask prototypes:

- `app.py` — standalone application and legacy v0 API
- `pirddiiqlab/backend.py` — packaged Flask application factory

The `app.py` entry point includes:

- `GET /health`
- `GET/POST /items`
- `GET/PUT/DELETE /items/<id>`
- `POST /update`
- `POST /init-db`
- `POST /imhotep/decision`

The SQLite prototype is suitable for local development and demonstrations. Production use requires a server database, migrations, authentication, authorization, audit controls, structured logging, and secure configuration.

## IMHOTEP decision engine

The repository includes `pirddiiqlab/decision_engine.py`, a deterministic rule-based decision engine for incoming operational payloads. It returns:

- `approve`
- `review`
- `escalate`
- `halt`

It is intended for operational experiments and is not a clinical decision tool.

## FootCare risk model package

`footcare_risk_model` provides an installable interface to the Diabetes Foot Complications Fine-Gray model.

```bash
pirddiiq-footcare-risk patients.csv scored_patients.csv --model footcare_risk_model/footcare_fgr_model.json --days 365.25 730.5
```

The repository does not include a validated clinical model artifact at runtime unless it has been obtained and verified. This package is research/educational software, not a diagnosis or substitute for clinical judgment.

## Future Chicago CGM access work

Planned work should remain staged and scoped:

1. Device-neutral and standards-based CGM data ingestion
2. Patient enrollment and secure consent workflows
3. Device and sensor supply inventory
4. Low-bandwidth and offline-friendly patient access
5. Assistance for insurance, Medicaid, transportation, and care navigation barriers
6. Clinician-reviewed alerts and escalation workflows
7. Administrative reporting with de-identification and minimum necessary access
8. Authentication, authorization, encryption, retention, and audit controls
9. Clinical, accessibility, privacy, and regulatory validation

No future alert or intake feature should claim that it is clinically effective until independently validated with qualified clinicians and appropriate oversight.

## Test coverage

Run the repository test suite:

```bash
python -m pip install -e '.[dev,rds]'
python -m pytest -q
```

Existing tests cover decision-engine behavior and FootCare model utilities. Synthetic CGM tests cover:

- Successful ingestion and retrieval
- Atomic rejection of invalid batches
- Timezone requirement
- Participant-query requirement
- Non-finite and boolean glucose rejection

Tests use synthetic data and do not establish medical validity or device accuracy.

## Branch and update history

The `feature/chicago-cgm-access` branch contains the first synthetic CGM prototype and documentation updates. It was created from `main` and added:

- A standalone CGM readings API
- Synthetic SQLite storage for local demonstrations
- A synthetic CSV dataset
- Google Colab instructions and notebook support
- API tests and safety documentation
- Eric Hilary Smith and the maintainer email in package metadata

## Security and privacy

Do not place credentials, tokens, secrets, identifiable patient records, or real CGM data in source control or hosted notebooks. Any credential previously committed to `Bard.py` should be considered compromised and revoked.

Additional production requirements include:

- Strong identity and role-based access controls
- Encryption in transit and at rest
- Data minimization and retention controls
- Audit logs for reads and writes
- Secure device integration and dependency monitoring
- Incident response and backup/recovery procedures
- Clinical and privacy governance

## Running the server

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,rds]'
python -m pirddiiqlab.cli --port 8080
```

The server listens on the `PORT` environment variable or port `8080` by default.

## License

See the repository license file for licensing terms.
