from unittest.mock import patch
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.main import app, get_session
from app.rate_limit import reset_rate_limits


def _override_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_session] = _override_session
client = TestClient(app)



@pytest.fixture(autouse=True)
def _reset_rate_limits():
    reset_rate_limits()


def test_create_repo_schedules_a_sync_for_a_new_repo():
    with patch("app.main._sync_repository_task") as mock_task:
        response = client.post("/repos", json={"owner": "octocat", "name": "hello"})

    assert response.status_code == 200
    body = response.json()
    assert body["owner"] == "octocat"
    assert body["status"] == "pending"
    mock_task.assert_called_once()


def test_create_repo_rejects_empty_owner():
    response = client.post("/repos", json={"owner": "", "name": "hello"})
    assert response.status_code == 400


def test_create_repo_rejects_missing_field():
    response = client.post("/repos", json={"owner": "octocat"})
    assert response.status_code == 422


def test_create_repo_is_rate_limited_after_three_requests():
    with patch("app.main._sync_repository_task"):
        for i in range(3):
            client.post("/repos", json={"owner": "octocat", "name": f"repo{i}"})
        response = client.post("/repos", json={"owner": "octocat", "name": "repo4"})

    assert response.status_code == 429


def test_get_repo_returns_404_for_unknown_repo():
    response = client.get("/repos/999")
    assert response.status_code == 404


def test_get_repo_returns_current_status():
    with patch("app.main._sync_repository_task"):
        created = client.post("/repos", json={"owner": "octocat", "name": "hello"}).json()

    response = client.get(f"/repos/{created['id']}")

    assert response.status_code == 200
    assert response.json()["status"] == "pending"


def test_metrics_endpoints_require_repo_id():
    response = client.get("/metrics/time-to-merge")
    assert response.status_code == 422




def test_metrics_endpoints_return_empty_lists_when_no_data():
    with patch("app.main._sync_repository_task"):
        created = client.post("/repos", json={"owner": "octocat", "name": "hello"}).json()

    repo_id = created["id"]
    assert client.get(f"/metrics/time-to-merge/{repo_id}").json() == []
    assert client.get(f"/metrics/review-turnaround/{repo_id}").json() == []
    assert client.get(f"/metrics/pr-size/{repo_id}").json() == []
