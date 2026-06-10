import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities as activities_db

initial_activities = copy.deepcopy(activities_db)

@pytest.fixture(autouse=True)
def reset_activities():
    activities_db.clear()
    activities_db.update(copy.deepcopy(initial_activities))


def test_get_activities_returns_all_activities():
    with TestClient(app) as client:
        response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert isinstance(payload["Chess Club"]["participants"], list)


def test_signup_adds_participant_successfully():
    new_email = "newstudent@mergington.edu"
    with TestClient(app) as client:
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": new_email}
        )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {new_email} for Chess Club"}
    assert new_email in activities_db["Chess Club"]["participants"]


def test_signup_missing_activity_returns_404():
    with TestClient(app) as client:
        response = client.post(
            "/activities/Unknown Activity/signup",
            params={"email": "student@mergington.edu"}
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_existing_participant_returns_400():
    existing_email = "michael@mergington.edu"
    with TestClient(app) as client:
        response = client.post(
            "/activities/Chess Club/signup",
            params={"email": existing_email}
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"
