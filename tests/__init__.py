import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict to its original state after each test."""
    yield
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


client = TestClient(app)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_200():
    response = client.get("/activities")
    assert response.status_code == 200


def test_get_activities_returns_dict():
    response = client.get("/activities")
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0


def test_get_activities_contains_expected_fields():
    response = client.get("/activities")
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "new@mergington.edu"},
    )
    assert response.status_code == 200
    assert "new@mergington.edu" in response.json()["message"]


def test_signup_adds_participant():
    client.post("/activities/Chess Club/signup", params={"email": "new@mergington.edu"})
    response = client.get("/activities")
    assert "new@mergington.edu" in response.json()["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    email = "michael@mergington.edu"  # already in Chess Club seed data
    response = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 400


def test_signup_unknown_activity_returns_404():
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "someone@mergington.edu"},
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    email = "michael@mergington.edu"  # seeded in Chess Club
    response = client.delete("/activities/Chess Club/signup", params={"email": email})
    assert response.status_code == 200
    assert email in response.json()["message"]


def test_unregister_removes_participant():
    email = "michael@mergington.edu"
    client.delete("/activities/Chess Club/signup", params={"email": email})
    response = client.get("/activities")
    assert email not in response.json()["Chess Club"]["participants"]


def test_unregister_not_registered_returns_404():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "ghost@mergington.edu"},
    )
    assert response.status_code == 404


def test_unregister_unknown_activity_returns_404():
    response = client.delete(
        "/activities/Nonexistent Club/signup",
        params={"email": "someone@mergington.edu"},
    )
    assert response.status_code == 404