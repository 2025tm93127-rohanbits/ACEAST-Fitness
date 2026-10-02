"""Unit + route tests for the ACEest Fitness Flask app."""

import pytest

from app import calculate_calories, calculate_bmi, PROGRAMS


# ---------------------------------------------------------------------------
# Business-logic unit tests (pure functions)
# ---------------------------------------------------------------------------
def test_calculate_calories_basic():
    # 80 kg on Muscle Gain (factor 35) -> 2800 kcal
    assert calculate_calories(80, 35) == 2800


def test_calculate_calories_rounds_down_to_int():
    # 70.5 * 22 = 1551.0 -> 1551
    assert calculate_calories(70.5, 22) == 1551
    assert isinstance(calculate_calories(70.5, 22), int)


@pytest.mark.parametrize("weight", [0, -5, None])
def test_calculate_calories_invalid_weight_returns_none(weight):
    assert calculate_calories(weight, 35) is None


def test_program_factors_match_original_app():
    # Factors carried over from Aceestver-2.2.4.py must not drift.
    assert PROGRAMS["Fat Loss (FL) - 3 day"]["factor"] == 22
    assert PROGRAMS["Fat Loss (FL) - 5 day"]["factor"] == 24
    assert PROGRAMS["Muscle Gain (MG) - PPL"]["factor"] == 35
    assert PROGRAMS["Beginner (BG)"]["factor"] == 26


def test_calculate_bmi_normal():
    bmi, category = calculate_bmi(180, 80)  # 80 / 1.8^2 = 24.7
    assert bmi == 24.7
    assert category == "Normal"


@pytest.mark.parametrize(
    "height,weight,expected_category",
    [
        (180, 55, "Underweight"),   # 16.98
        (180, 80, "Normal"),        # 24.7
        (180, 90, "Overweight"),    # 27.8
        (180, 110, "Obese"),        # 33.9
    ],
)
def test_calculate_bmi_categories(height, weight, expected_category):
    _, category = calculate_bmi(height, weight)
    assert category == expected_category


@pytest.mark.parametrize("height,weight", [(0, 80), (180, 0), (None, None)])
def test_calculate_bmi_invalid_returns_none(height, weight):
    bmi, category = calculate_bmi(height, weight)
    assert bmi is None and category is None


# ---------------------------------------------------------------------------
# Route / integration tests (Flask test client)
# ---------------------------------------------------------------------------
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"ACEest Fitness" in resp.data


def test_clients_page_empty(client):
    resp = client.get("/clients")
    assert resp.status_code == 200


def test_programs_page_lists_programs(client):
    resp = client.get("/programs")
    assert resp.status_code == 200
    assert b"Muscle Gain" in resp.data


def test_progress_page(client):
    resp = client.get("/progress")
    assert resp.status_code == 200


def test_add_client_get(client):
    resp = client.get("/clients/add")
    assert resp.status_code == 200
    assert b"Add Client" in resp.data


def test_add_valid_client_and_calories(client):
    resp = client.post(
        "/clients/add",
        data={
            "name": "John",
            "age": "30",
            "height": "180",
            "weight": "80",
            "program": "Muscle Gain (MG) - PPL",
            "target_weight": "85",
            "target_adherence": "90",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"John" in resp.data
    # 80 * 35 = 2800
    assert b"2800" in resp.data


def test_add_client_missing_name(client):
    resp = client.post(
        "/clients/add",
        data={"name": "", "program": "Beginner (BG)"},
    )
    assert resp.status_code == 400
    assert b"Name is required" in resp.data


def test_add_client_non_numeric_weight(client):
    resp = client.post(
        "/clients/add",
        data={"name": "BadWeight", "program": "Beginner (BG)", "weight": "abc"},
    )
    assert resp.status_code == 400
    assert b"Weight must be a number" in resp.data


def test_add_client_unknown_program(client):
    resp = client.post(
        "/clients/add",
        data={"name": "NoProg", "program": "Does Not Exist"},
    )
    assert resp.status_code == 400
    assert b"Unknown program" in resp.data


def test_add_duplicate_client(client):
    data = {"name": "Dup", "program": "Beginner (BG)"}
    client.post("/clients/add", data=data, follow_redirects=True)
    resp = client.post("/clients/add", data=data)
    assert resp.status_code == 400
    assert b"already exists" in resp.data


def test_client_detail_shows_bmi(client):
    client.post(
        "/clients/add",
        data={
            "name": "BmiGuy",
            "height": "180",
            "weight": "80",
            "program": "Beginner (BG)",
        },
        follow_redirects=True,
    )
    resp = client.get("/clients/1")
    assert resp.status_code == 200
    assert b"24.7" in resp.data
    assert b"Normal" in resp.data


def test_client_detail_not_found_redirects(client):
    resp = client.get("/clients/999", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Client not found" in resp.data


def test_record_progress_valid(client):
    client.post(
        "/clients/add",
        data={"name": "ProgGuy", "program": "Beginner (BG)"},
        follow_redirects=True,
    )
    resp = client.post(
        "/progress",
        data={"client_name": "ProgGuy", "adherence": "75"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"75" in resp.data


def test_record_progress_unknown_client(client):
    resp = client.post(
        "/progress",
        data={"client_name": "Ghost", "adherence": "50"},
    )
    assert resp.status_code == 200
    assert b"does not exist" in resp.data


def test_record_progress_adherence_over_100(client):
    client.post(
        "/clients/add",
        data={"name": "OverGuy", "program": "Beginner (BG)"},
        follow_redirects=True,
    )
    resp = client.post(
        "/progress",
        data={"client_name": "OverGuy", "adherence": "150"},
    )
    assert resp.status_code == 200
    assert b"cannot exceed 100" in resp.data
