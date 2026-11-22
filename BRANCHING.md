# Branching, Versioning and Release Strategy

This repository uses a lightweight **Git Flow** model with **Semantic
Versioning**. Every release is traceable from Git tag to container image to
Kubernetes deployment.

## Branches

| Branch        | Purpose                                         | Created from | Merges into          |
|---------------|-------------------------------------------------|--------------|----------------------|
| `main`        | Production-ready code. Every commit is released and tagged. | -  | -                    |
| `develop`     | Integration branch for the next release.        | `main`       | `release/*`          |
| `feature/*`   | New features, e.g. `feature/app-versioning`.    | `develop`    | `develop` (PR)       |
| `docs/*`, `ci/*`, `chore/*` | Docs, pipeline and housekeeping changes. | `develop` | `develop` (PR)   |
| `release/X.Y.Z` | Release hardening: version bump, changelog, fixes only. | `develop` | `main` + `develop` |
| `hotfix/X.Y.Z`  | Urgent production fix.                        | `main`       | `main` + `develop`   |

Rules:

- No direct pushes to `main` or `develop`; all changes go through pull requests.
- A PR must have a green CI run (pytest + Docker build + container smoke test)
  before merge. Jenkins additionally enforces the SonarQube quality gate.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `build:`, `ci:`, `docs:`, `test:`, `chore:`).

## Versioning

Versions follow `MAJOR.MINOR.PATCH`:

- **MAJOR** - incompatible change (e.g. database schema change requiring migration).
- **MINOR** - new backwards-compatible feature.
- **PATCH** - bug fix.

The single source of truth is `__version__` in `app.py`. It is mirrored by:

| Artifact             | Example                                                  |
|----------------------|----------------------------------------------------------|
| Git tag (annotated)  | `v1.1.0`                                                 |
| Container image tags | `ghcr.io/2025tm93127-rohanbits/aceest-fitness:1.1.0`, `:1.1.0-<build>`, `:<git-sha>`, `:latest` |
| Running app          | `GET /version` -> `{"version": "1.1.0", ...}`           |
| SonarQube            | `sonar.projectVersion=1.1.0`                             |

## Release history

| Version  | Content                                                                 |
|----------|-------------------------------------------------------------------------|
| `v1.0.0` | Assignment 1 baseline: Flask port of desktop app v2.2.4, pytest, Docker, Jenkins, GitHub Actions. |
| `v1.1.0` | `/health`, `/version`, version/variant in UI, coverage + SonarQube config. |

The original Tkinter desktop versions (1.0 - 3.2.4) that the web app evolved
from are kept under `legacy/desktop/` for reference.

## Release procedure

```bash
# 1. Cut the release branch from develop
git checkout develop && git pull
git checkout -b release/1.2.0

# 2. Bump __version__ in app.py and sonar.projectVersion, update CHANGELOG.md
git commit -am "chore(release): 1.2.0"

# 3. PR release/1.2.0 -> main, merge after CI + quality gate pass

# 4. Tag the merge commit on main and push the tag
git checkout main && git pull
git tag -a v1.2.0 -m "v1.2.0"
git push origin v1.2.0

# 5. Back-merge into develop
git checkout develop && git merge --no-ff main && git push
```

Pushing the tag triggers the pipeline that builds, tests and pushes the
versioned image to GitHub Container Registry.

## Rollback

Because every version is an immutable image tag, rolling back means
redeploying the previous tag (or `kubectl rollout undo`); no rebuild is
needed. Git history is never rewritten on `main`; a bad release is reverted
with `git revert` and released as a new PATCH version.
