from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.main import app, get_session


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


def test_ingest_endpoint(monkeypatch):
    monkeypatch.setenv("GITHUB_REPO", "octocat/hello")
    with patch("app.main.sync_repository", return_value={"pull_requests": 3, "reviews": 5}):
        response = client.post("/ingest")
    assert response.status_code == 200
    assert response.json() == {"pull_requests": 3, "reviews": 5}


def test_metrics_endpoints_return_empty_lists_when_no_data():
    assert client.get("/metrics/time-to-merge").json() == []
    assert client.get("/metrics/review-turnaround").json() == []
    assert client.get("/metrics/pr-size").json() == []
