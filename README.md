# ACEest Fitness & Gym

[![CI](https://github.com/2025tm93127-rohanbits/ACEAST-Fitness/actions/workflows/main.yml/badge.svg)](https://github.com/2025tm93127-rohanbits/ACEAST-Fitness/actions/workflows/main.yml)

A Flask web application for **ACEest Fitness & Gym**, built for the
*Introduction to DevOps* assignment (CSIZG514 / SEZG514). It is a web port of
the original ACEest Fitness desktop (Tkinter) application, re-engineered as a
small, testable, containerised service with a full CI pipeline.

---

## Table of Contents

1. [Features](#features)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Local Setup & Execution](#local-setup--execution)
5. [Running the Tests Manually](#running-the-tests-manually)
6. [Running with Docker](#running-with-docker)
7. [Configuration](#configuration)
8. [Application Routes](#application-routes)
9. [CI/CD Integration Logic](#cicd-integration-logic)
   - [GitHub Actions](#github-actions)
   - [Jenkins](#jenkins)

---

## Features

- **Dashboard** — ACEest branding and navigation.
- **Client Management** — add, list, and view clients with server-side input
  validation (required name, numeric/positive numbers, unique names).
- **Fitness Programs** — Fat Loss (3 & 5 day), Muscle Gain (PPL), Beginner.
- **Calorie Calculation** — daily target = `weight (kg) × program factor`
  (factors carried from the original app: FL-3d **22**, FL-5d **24**,
  MG-PPL **35**, Beginner **26**).
- **BMI** — calculated with risk category (Underweight / Normal / Overweight / Obese).
- **Progress / Adherence** — record and view weekly adherence per client.
- **SQLite** storage — no external database server required.

## Tech Stack

| Layer        | Technology                         |
|--------------|------------------------------------|
| Language     | Python 3.12                        |
| Web framework| Flask 3                            |
| Templating   | Jinja2 + static CSS                |
| Database     | SQLite (standard library `sqlite3`)|
| WSGI server  | gunicorn (in Docker image)         |
| Testing      | pytest                             |
| CI/CD        | GitHub Actions, Jenkins            |
| Container    | Docker (`python:3.12-slim`)        |

## Project Structure

```
aceest-fitness/
├── app.py                      # Flask app: application factory + routes + business logic
├── requirements.txt            # Runtime dependencies (Flask, gunicorn)
├── requirements-dev.txt        # Dev/test dependencies (pytest)
├── pytest.ini                  # Pytest configuration
├── Dockerfile                  # Container image definition
├── .dockerignore               # Files excluded from the image build context
├── Jenkinsfile                 # Jenkins declarative pipeline
├── README.md
├── .github/
│   └── workflows/
│       └── main.yml            # GitHub Actions CI workflow
├── templates/                  # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── clients.html
│   ├── add_client.html
│   ├── client_detail.html
│   ├── programs.html
│   └── progress.html
├── static/
│   └── style.css
└── tests/
    ├── conftest.py             # Pytest fixtures (app + test client, isolated temp DB)
    └── test_app.py             # Unit + route tests
```

---

## Local Setup & Execution

**Prerequisites:** Python 3.10+ installed.

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in a browser.

> The SQLite database file (`aceest_fitness.db`) is created automatically on
> first run.

---

## Running the Tests Manually

The test suite uses **pytest** and runs against an isolated temporary SQLite
database per test (no effect on your real data).

### Windows

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements-dev.txt
pytest
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pytest
```

Expected result: **all tests pass** (29 tests). For a quiet summary use
`pytest -q`; for verbose output use `pytest -v` (verbose is the default via
`pytest.ini`).

**What the tests cover**

- Business logic: calorie calculation (incl. integer rounding and invalid
  weight), BMI value + category boundaries, and program-factor integrity.
- Routes: home, clients list, add-client (valid save, missing name, non-numeric
  input, unknown program, duplicate name), client detail (BMI display,
  not-found redirect), programs page, and progress (valid record, unknown
  client, adherence over 100%).

---

## Running with Docker

The image serves the app with **gunicorn** on port 5000 and runs as a
non-root user.

```bash
docker build -t aceest-fitness .
docker run -p 5000:5000 aceest-fitness
```

Then open **http://127.0.0.1:5000**.

The SQLite database is written to `/app/data` inside the container. To persist
it across container restarts, mount a volume:

```bash
docker run -p 5000:5000 -v aceest_data:/app/data aceest-fitness
```

**Docker efficiency / security notes**

- Slim base image (`python:3.12-slim`) keeps the image small.
- Dependencies are installed in a separate, cached layer before source is
  copied, so code changes don't re-install packages.
- `pip install --no-cache-dir` avoids caching wheels in the image.
- `.dockerignore` keeps tests, venvs, Git metadata, and the local DB out of the
  build context.
- The container runs as a dedicated **non-root** user (`appuser`).

---

## Configuration

All configuration is via environment variables (no machine-specific paths or
secrets are hard-coded).

| Env var         | Purpose                             | Default               |
|-----------------|-------------------------------------|-----------------------|
| `ACEEST_DB`     | SQLite database file path           | `aceest_fitness.db`   |
| `ACEEST_SECRET` | Flask secret key (flash messages)   | `aceest-dev-key`      |

---

## Application Routes

| Method   | Path             | Purpose                           |
|----------|------------------|-----------------------------------|
| GET      | `/`              | Dashboard                         |
| GET      | `/clients`       | List clients                      |
| GET/POST | `/clients/add`   | Add a client                      |
| GET      | `/clients/<id>`  | Client detail (calories + BMI)    |
| GET      | `/programs`      | List programs and calorie factors |
| GET/POST | `/progress`      | Record / view weekly progress     |

---

## CI/CD Integration Logic

This project is wired for two independent CI/CD systems. Both perform the same
core quality gate: **install dependencies → run the pytest suite → build the
Docker image**. A build is considered green only if tests pass and the image
builds.

### GitHub Actions

Defined in **`.github/workflows/main.yml`**.

- **Trigger:** every `push` and every `pull_request` targeting the `main`
  branch.
- **Job `test`** (runner: `ubuntu-latest`):
  1. `actions/checkout@v4` — check out the repository.
  2. `actions/setup-python@v5` — install Python 3.12 with pip caching.
  3. Install dependencies from `requirements-dev.txt`.
  4. Run `pytest -v`.
- **Job `docker-build`** (runner: `ubuntu-latest`, `needs: test`):
  - Runs only after `test` succeeds, enforcing *test-before-build*.
  - Checks out the code and runs `docker build` to confirm the image builds
    cleanly.

The CI status badge at the top of this README reflects the latest run on
`main`. Because the build gate runs on every push, a failing test or a broken
Dockerfile blocks the pipeline immediately.

### Jenkins

Defined in **`Jenkinsfile`** (declarative pipeline), intended for a Linux
agent with `python3` and `docker` available.

**Stages**

1. **Checkout** — pull the source via `checkout scm`.
2. **Set up Python & install dependencies** — create a virtualenv and install
   `requirements-dev.txt`.
3. **Run tests (pytest)** — execute the suite and emit a JUnit report
   (`test-results.xml`), published with the `junit` step so results appear in
   the Jenkins UI.
4. **Build Docker image** — tag the image with the Jenkins build number and
   `latest`.

**Pipeline options & post actions**

- `timestamps()` on logs and `disableConcurrentBuilds()` to avoid overlapping
  runs.
- `post` blocks report success/failure and run `cleanWs()` to clean the
  workspace after each build.

**To run it in Jenkins:** create a *Pipeline* job → *Pipeline script from SCM*
→ point it at this repository's Git URL with script path `Jenkinsfile`. Ensure
the agent has Docker installed for the final stage. Enable *GitHub hook trigger
for GITScm polling* (or poll SCM) so the build triggers automatically on push.
