# Legacy desktop versions (reference only)

These are the original ACEest Fitness & Gym **Tkinter desktop** scripts the
Flask web application was re-engineered from. They are kept unchanged for
traceability and are **not** part of the build, tests, image or deployment
(excluded via `.dockerignore` and `sonar-project.properties`).

| File                  | Highlights                                              |
|-----------------------|---------------------------------------------------------|
| `Aceestver-1.0.py`    | First prototype: program display                         |
| `Aceestver-1.1.py`    | Client details, calorie estimate                         |
| `Aceestver1.1.2.py`   | UI refinements                                           |
| `Aceestver2.0.1.py`   | SQLite persistence                                       |
| `Aceestver-2.1.2.py`  | Persistence fixes                                        |
| `Aceestver-2.2.1.py`  | Progress tracking                                        |
| `Aceestver-2.2.4.py`  | Most complete stable version; **basis of the Flask app (web v1.0.0)** |
| `Aceestver-3.0.1.py`  | 3.x line start (same feature set as 2.2.4)               |
| `Aceestver-3.1.2.py`  | Login / roles                                            |
| `Aceestver-3.2.4.py`  | Further 3.x changes                                      |

Mapping desktop features to web releases is described in `BRANCHING.md`.
