"""
ACEest Fitness & Gym - Flask web application.

This is the DevOps-assignment Flask port of the original ACEest desktop
(Tkinter) application. The business logic is taken from the most complete
stable desktop version (Aceestver-2.2.4.py):

  * Clients with name / age / height / weight / program / goals
  * Program-based calorie targets:  calories = weight(kg) * program_factor
  * BMI calculation and risk category
  * Weekly adherence / progress tracking

No login/auth or PDF/AI features from the 3.x versions are included: the
assignment asks for a small, testable, containerisable app and explicitly
says not to add authentication unless the core functionality needs it.
"""

import os
import sqlite3
from datetime import datetime

from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
    url_for,
    flash,
)

# ---------------------------------------------------------------------------
# Business data (carried over from Aceestver-2.2.4.py)
# ---------------------------------------------------------------------------
# Each program has a calorie "factor". Daily calorie target = weight * factor.
PROGRAMS = {
    "Fat Loss (FL) - 3 day": {
        "factor": 22,
        "desc": "3-day full-body fat loss",
    },
    "Fat Loss (FL) - 5 day": {
        "factor": 24,
        "desc": "5-day split, higher volume fat loss",
    },
    "Muscle Gain (MG) - PPL": {
        "factor": 35,
        "desc": "Push/Pull/Legs hypertrophy",
    },
    "Beginner (BG)": {
        "factor": 26,
        "desc": "3-day simple beginner full-body",
    },
}

# Default database file lives next to this file, but can be overridden with
# the ACEEST_DB environment variable (useful for tests / containers).
DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aceest_fitness.db")


# ---------------------------------------------------------------------------
# Business-logic helpers (pure functions -> easy to unit test later)
# ---------------------------------------------------------------------------
def calculate_calories(weight, factor):
    """Daily calorie target = weight(kg) * program factor (from the original app)."""
    if weight is None or weight <= 0:
        return None
    return int(weight * factor)


def calculate_bmi(height_cm, weight_kg):
    """BMI = weight(kg) / height(m)^2. Returns (bmi, category) or (None, None)."""
    if not height_cm or not weight_kg or height_cm <= 0 or weight_kg <= 0:
        return None, None
    h_m = height_cm / 100.0
    bmi = round(weight_kg / (h_m * h_m), 1)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return bmi, category


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    """Return a per-request SQLite connection (stored on flask.g)."""
    if "db" not in g:
        g.db = sqlite3.connect(current_db_path())
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def current_db_path():
    """DB path for the active app (set in create_app)."""
    from flask import current_app

    return current_app.config["DATABASE"]


def init_db(app):
    """Create tables if they do not exist."""
    with app.app_context():
        db = sqlite3.connect(app.config["DATABASE"])
        cur = db.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                age INTEGER,
                height REAL,
                weight REAL,
                program TEXT,
                calories INTEGER,
                target_weight REAL,
                target_adherence INTEGER
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                week TEXT,
                adherence INTEGER
            )
            """
        )
        db.commit()
        db.close()


# ---------------------------------------------------------------------------
# Validation helper
# ---------------------------------------------------------------------------
def _parse_optional_number(raw, cast, field, errors, minimum=0):
    """Parse an optional numeric form field. Returns None if blank."""
    raw = (raw or "").strip()
    if raw == "":
        return None
    try:
        value = cast(raw)
    except (ValueError, TypeError):
        errors.append(f"{field} must be a number.")
        return None
    if value < minimum:
        errors.append(f"{field} cannot be negative.")
        return None
    return value


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------
def create_app(database=None):
    app = Flask(__name__)
    app.config["DATABASE"] = database or os.environ.get("ACEEST_DB", DEFAULT_DB)
    # Secret key only needed for flash messages; not a real secret.
    app.config["SECRET_KEY"] = os.environ.get("ACEEST_SECRET", "aceest-dev-key")

    app.teardown_appcontext(close_db)
    init_db(app)

    # ---------------- Routes ----------------

    @app.route("/")
    def index():
        db = get_db()
        client_count = db.execute("SELECT COUNT(*) AS c FROM clients").fetchone()["c"]
        program_count = len(PROGRAMS)
        return render_template(
            "index.html",
            client_count=client_count,
            program_count=program_count,
        )

    @app.route("/clients")
    def clients():
        db = get_db()
        rows = db.execute("SELECT * FROM clients ORDER BY name").fetchall()
        return render_template("clients.html", clients=rows)

    @app.route("/clients/add", methods=["GET", "POST"])
    def add_client():
        if request.method == "POST":
            errors = []
            name = (request.form.get("name") or "").strip()
            program = (request.form.get("program") or "").strip()

            if not name:
                errors.append("Name is required.")
            if not program:
                errors.append("Program is required.")
            elif program not in PROGRAMS:
                errors.append("Unknown program selected.")

            age = _parse_optional_number(request.form.get("age"), int, "Age", errors)
            height = _parse_optional_number(
                request.form.get("height"), float, "Height", errors
            )
            weight = _parse_optional_number(
                request.form.get("weight"), float, "Weight", errors
            )
            target_weight = _parse_optional_number(
                request.form.get("target_weight"), float, "Target weight", errors
            )
            target_adherence = _parse_optional_number(
                request.form.get("target_adherence"), int, "Target adherence", errors
            )
            if target_adherence is not None and target_adherence > 100:
                errors.append("Target adherence cannot exceed 100%.")

            if errors:
                for e in errors:
                    flash(e, "error")
                return (
                    render_template(
                        "add_client.html",
                        programs=PROGRAMS,
                        form=request.form,
                    ),
                    400,
                )

            factor = PROGRAMS[program]["factor"]
            calories = calculate_calories(weight, factor)

            db = get_db()
            try:
                db.execute(
                    """
                    INSERT INTO clients
                        (name, age, height, weight, program, calories,
                         target_weight, target_adherence)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        name,
                        age,
                        height,
                        weight,
                        program,
                        calories,
                        target_weight,
                        target_adherence,
                    ),
                )
                db.commit()
            except sqlite3.IntegrityError:
                flash(f"A client named '{name}' already exists.", "error")
                return (
                    render_template(
                        "add_client.html",
                        programs=PROGRAMS,
                        form=request.form,
                    ),
                    400,
                )

            flash(f"Client '{name}' added successfully.", "success")
            return redirect(url_for("clients"))

        return render_template("add_client.html", programs=PROGRAMS, form={})

    @app.route("/clients/<int:client_id>")
    def client_detail(client_id):
        db = get_db()
        client = db.execute(
            "SELECT * FROM clients WHERE id = ?", (client_id,)
        ).fetchone()
        if client is None:
            flash("Client not found.", "error")
            return redirect(url_for("clients"))

        bmi, bmi_category = calculate_bmi(client["height"], client["weight"])
        program_desc = PROGRAMS.get(client["program"], {}).get("desc", "")

        progress_rows = db.execute(
            "SELECT * FROM progress WHERE client_name = ? ORDER BY id",
            (client["name"],),
        ).fetchall()
        if progress_rows:
            avg_adherence = round(
                sum(r["adherence"] for r in progress_rows) / len(progress_rows), 1
            )
        else:
            avg_adherence = None

        return render_template(
            "client_detail.html",
            client=client,
            bmi=bmi,
            bmi_category=bmi_category,
            program_desc=program_desc,
            progress=progress_rows,
            avg_adherence=avg_adherence,
        )

    @app.route("/programs")
    def programs():
        return render_template("programs.html", programs=PROGRAMS)

    @app.route("/progress", methods=["GET", "POST"])
    def progress():
        db = get_db()
        if request.method == "POST":
            errors = []
            client_name = (request.form.get("client_name") or "").strip()
            if not client_name:
                errors.append("Please select a client.")
            else:
                exists = db.execute(
                    "SELECT 1 FROM clients WHERE name = ?", (client_name,)
                ).fetchone()
                if not exists:
                    errors.append("Selected client does not exist.")

            adherence = _parse_optional_number(
                request.form.get("adherence"), int, "Adherence", errors
            )
            if adherence is None:
                errors.append("Adherence is required.")
            elif adherence > 100:
                errors.append("Adherence cannot exceed 100%.")

            if errors:
                for e in errors:
                    flash(e, "error")
            else:
                week = datetime.now().strftime("Week %U - %Y")
                db.execute(
                    "INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
                    (client_name, week, adherence),
                )
                db.commit()
                flash(f"Progress recorded for '{client_name}'.", "success")
                return redirect(url_for("progress"))

        client_rows = db.execute("SELECT name FROM clients ORDER BY name").fetchall()
        progress_rows = db.execute(
            "SELECT * FROM progress ORDER BY id DESC"
        ).fetchall()
        return render_template(
            "progress.html",
            clients=client_rows,
            progress=progress_rows,
        )

    return app


# Module-level app so `python app.py` and `flask run` both work.
app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
