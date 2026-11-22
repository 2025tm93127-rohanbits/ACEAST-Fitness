"""Tests for operational endpoints (/health, /version) and release metadata.

These endpoints back the Kubernetes liveness/readiness probes and let the
deployment strategies (blue-green, canary, A/B, shadow) be observed from
outside the cluster, so they are part of the deployment contract.
"""

import re

import app as app_module
from app import create_app, get_app_version, get_build_info


def test_version_constant_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", app_module.__version__)


def test_app_version_defaults_to_code_version(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    assert get_app_version() == app_module.__version__


def test_app_version_env_override(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "9.9.9")
    assert get_app_version() == "9.9.9"


def test_build_info_defaults(monkeypatch):
    for var in ("APP_VERSION", "APP_VARIANT", "GIT_COMMIT"):
        monkeypatch.delenv(var, raising=False)
    assert get_build_info() == {
        "version": app_module.__version__,
        "variant": "stable",
        "commit": "unknown",
    }


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["version"] == get_app_version()


def test_health_reports_503_when_database_unavailable(tmp_path):
    application = create_app(database=str(tmp_path / "ok.db"))
    application.config.update(TESTING=True)
    # Point the app at a directory: sqlite cannot open it -> probe must fail.
    application.config["DATABASE"] = str(tmp_path)
    resp = application.test_client().get("/health")
    assert resp.status_code == 503
    assert resp.get_json() == {"status": "error", "database": "unavailable"}


def test_version_endpoint_reflects_environment(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "2.0.0")
    monkeypatch.setenv("APP_VARIANT", "canary")
    monkeypatch.setenv("GIT_COMMIT", "abc1234")
    resp = client.get("/version")
    assert resp.status_code == 200
    assert resp.get_json() == {
        "version": "2.0.0",
        "variant": "canary",
        "commit": "abc1234",
    }


def test_footer_shows_version_and_variant(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "3.1.4")
    monkeypatch.setenv("APP_VARIANT", "green")
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"v3.1.4" in resp.data
    assert b"green" in resp.data
