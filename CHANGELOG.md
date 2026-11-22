# Changelog

All notable changes to ACEest Fitness & Gym are documented here.
The project follows [Semantic Versioning](https://semver.org/); every release
is a Git tag `vX.Y.Z` and a container image tag `X.Y.Z` in GitHub Container
Registry (`ghcr.io/2025tm93127-rohanbits/aceest-fitness`).

## [Unreleased]

## [1.1.0]

### Added
- `/health` endpoint (app + database check, HTTP 503 when the DB is
  unavailable) for Kubernetes liveness/readiness probes.
- `/version` endpoint returning version, deployment variant and Git commit.
- Version and deployment variant shown in the page footer, so blue-green,
  canary and A/B deployments can be told apart in the browser.
- `APP_VERSION`, `APP_VARIANT`, `GIT_COMMIT` environment variables.
- Test coverage reporting (`pytest-cov`, `.coveragerc`) and
  `sonar-project.properties` for SonarQube analysis.
- Docker image OCI labels, version build args and a `HEALTHCHECK`.
- 8 new tests for the operational endpoints (37 total).

### Changed
- GitHub Actions runs on `main`, `develop`, `release/**`, `hotfix/**`, tags
  and PRs to `main`/`develop`; publishes test and coverage reports and
  smoke-tests the built container.

## [1.0.0]

### Added
- Flask port of the ACEest desktop app (client management, programs, calorie
  and BMI calculation, weekly progress tracking) on SQLite.
- Pytest suite (29 tests), Dockerfile, Jenkins pipeline, GitHub Actions CI.
