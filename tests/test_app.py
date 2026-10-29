import copy

import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", copy.deepcopy(app_module.activities))
    return TestClient(app_module.app)


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Art%20Club/signup",
        params={"email": "student@example.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up student@example.edu for Art Club"
    }
    assert "student@example.edu" in app_module.activities["Art Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    email = "student@example.edu"
    signup_url = "/activities/Art%20Club/signup"
    client.post(signup_url, params={"email": email})

    response = client.post(signup_url, params={"email": email})

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities["Art Club"]["participants"].count(email) == 1


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    email = "student@example.edu"
    app_module.activities["Art Club"]["participants"].append(email)

    response = client.delete(
        "/activities/Art%20Club/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@example.edu from Art Club"
    }
    assert email not in app_module.activities["Art Club"]["participants"]


def test_unregister_rejects_unregistered_participant(client):
    response = client.delete(
        "/activities/Art%20Club/signup",
        params={"email": "student@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@example.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
