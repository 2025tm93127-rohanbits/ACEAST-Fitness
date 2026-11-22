# Legacy desktop versions (reference only)

These are the original ACEest Fitness & Gym **Tkinter desktop** scripts the
Flask web application was re-engineered from. They are kept unchanged for
traceability and are **not** part of the build, tests, image or deployment
(excluded via `.dockerignore` and `sonar-project.properties`).

| File                  | Highlights                                              |
|-----------------------|---------------------------------------------------------|
| `Aceestver-1.0.py`    | First prototype: program / workout display              |
| `Aceestver-1.1.py`    | Client details, calorie estimate, progress              |
| `Aceestver1.1.2.py`   | CSV export, matplotlib progress chart                   |
| `Aceestver2.0.1.py`   | SQLite persistence                                      |
| `Aceestver-2.1.2.py`  | Identical to 2.0.1                                      |
| `Aceestver-2.2.1.py`  | Progress tracking with charts on SQLite                 |
| `Aceestver-2.2.4.py`  | Most complete stable version (BMI, workouts, progress); **basis of the Flask app (web v1.0.0)** |
| `Aceestver-3.0.1.py`  | Identical to 2.2.4                                      |
| `Aceestver-3.1.2.py`  | Login / roles, membership, PDF reports                  |
| `Aceestver-3.2.4.py`  | Reworked 3.x: login, membership, PDF, workouts          |

Mapping desktop features to web releases is described in `BRANCHING.md`.
