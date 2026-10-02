# ACEest Fitness & Gym

Flask web application for the *Introduction to DevOps* assignment
(CSIZG514 / SEZG514). A web port of the original ACEest Fitness & Gym
desktop app, built to be easy to run, test, containerise, and build in CI.

## Features

- **Dashboard** with branding and navigation
- **Client management** — add / list / view clients with input validation
- **Fitness programs** — Fat Loss (3 & 5 day), Muscle Gain (PPL), Beginner
- **Calorie calculation** — daily target = `weight (kg) × program factor`
  (factors: FL-3d 22, FL-5d 24, MG-PPL 35, Beginner 26)
- **BMI** calculation with risk category
- **Weekly progress / adherence** tracking
- **SQLite** storage (no external database server)

## Tech stack

- Python 3, Flask
- SQLite (standard library `sqlite3`)
- Jinja2 templates + static CSS

## Project structure

```
aceest-fitness/
├── app.py              # Flask app (application factory + routes)
├── requirements.txt
├── templates/          # Jinja2 templates
├── static/style.css
└── README.md
```

## Run locally (Windows)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000

## Run locally (macOS / Linux)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## Run with Docker

```bash
docker build -t aceest-fitness .
docker run -p 5000:5000 aceest-fitness
```

Then open http://127.0.0.1:5000

The image serves the app with gunicorn on port 5000. The SQLite database
is written to `/app/data` inside the container; mount a volume to persist it:

```bash
docker run -p 5000:5000 -v aceest_data:/app/data aceest-fitness
```

## Run tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Configuration

| Env var        | Purpose                        | Default                 |
|----------------|--------------------------------|-------------------------|
| `ACEEST_DB`    | SQLite database file path      | `aceest_fitness.db`     |
| `ACEEST_SECRET`| Flask secret (flash messages)  | `aceest-dev-key`        |

## Routes

| Method   | Path                  | Purpose                      |
|----------|-----------------------|------------------------------|
| GET      | `/`                   | Dashboard                    |
| GET      | `/clients`            | List clients                 |
| GET/POST | `/clients/add`        | Add a client                 |
| GET      | `/clients/<id>`       | Client detail (calories/BMI) |
| GET      | `/programs`           | List programs                |
| GET/POST | `/progress`           | Record / view progress       |
