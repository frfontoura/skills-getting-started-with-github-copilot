import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    # Arrange: snapshot activities to restore after test
    original = copy.deepcopy(activities)
    client = TestClient(app)
    yield client
    # Teardown: restore original in-memory activities
    activities.clear()
    activities.update(original)


def test_get_activities(client):
    # Act
    resp = client.get("/activities")

    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_success(client):
    email = "newstudent@mergington.edu"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in activities["Chess Club"]["participants"]


def test_signup_nonexistent_activity(client):
    resp = client.post("/activities/NoSuchActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404


def test_signup_already_registered(client):
    # michael@mergington.edu is already registered for Chess Club
    email = "michael@mergington.edu"
    resp = client.post("/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 400


def test_unregister_success(client):
    email = "michael@mergington.edu"
    resp = client.delete("/activities/Chess Club/unregister", params={"email": email})
    assert resp.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_not_registered(client):
    resp = client.delete("/activities/Chess Club/unregister", params={"email": "ghost@mergington.edu"})
    assert resp.status_code == 400


def test_root_redirect(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307)
    assert resp.headers.get("location", "").endswith("/static/index.html")
