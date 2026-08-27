from unittest.mock import patch

from app.ingest import sync_repository, run_repository_sync
from app.models import PullRequest, Review, Repository


FAKE_PRS = [
    {
        "number": 1,
        "title": "Fix bug",
        "author": "octocat",
        "created_at": "2026-01-01T00:00:00Z",
        "merged_at": "2026-01-02T00:00:00Z",
        "closed_at": "2026-01-02T00:00:00Z",
    }
]

FAKE_DETAIL = {"additions": 10, "deletions": 2, "changed_files": 1}

FAKE_REVIEWS = [
    {"reviewer": "hubot", "state": "APPROVED", "submitted_at": "2026-01-01T12:00:00Z"}
]

def _make_repo(session):
    repo = Repository(owner="octocat", name="hello", status="pending")
    session.add(repo)
    session.commit()
    return repo

def test_sync_repository_inserts_prs_and_reviews(session):
    repo = _make_repo(session)
    with patch("app.ingest.fetch_pull_requests", return_value=FAKE_PRS), patch(
        "app.ingest.fetch_pull_request_detail", return_value=FAKE_DETAIL
    ), patch("app.ingest.fetch_reviews", return_value=FAKE_REVIEWS):
        result = sync_repository(session, repo.id, "octocat", "hello", token=None)

    assert result == {"pull_requests": 1, "reviews": 1}
    assert session.query(PullRequest).filter_by(repo_id=repo.id).count() == 1
    assert session.query(Review).count() == 1


def test_sync_repository_is_idempotent(session):
    repo = _make_repo(session)
    with patch("app.ingest.fetch_pull_requests", return_value=FAKE_PRS), patch(
        "app.ingest.fetch_pull_request_detail", return_value=FAKE_DETAIL
    ), patch("app.ingest.fetch_reviews", return_value=FAKE_REVIEWS):
        sync_repository(session, repo.id, "octocat", "hello", token=None)
        sync_repository(session, repo.id, "octocat", "hello", token=None)

    assert session.query(PullRequest).filter_by(repo_id=repo.id).count() == 1
    assert session.query(Review).count() == 1

def test_sync_repository_caps_at_max_prs(session):
    repo = _make_repo(session)
    many_prs = [{**FAKE_PRS[0], "number": i} for i in range(1, 250)]
    with patch("app.ingest.fetch_pull_requests", return_value=many_prs), patch(
        "app.ingest.fetch_pull_request_detail", return_value=FAKE_DETAIL
    ), patch("app.ingest.fetch_reviews", return_value=FAKE_REVIEWS):
        result = sync_repository(session, repo.id, "octocat", "hello", token=None)

    assert result["pull_requests"] == 200
    assert session.query(PullRequest).filter_by(repo_id=repo.id).count() == 200

def test_run_repository_sync_marks_repo_ready(session):
    repo = _make_repo(session)
    with patch("app.ingest.fetch_pull_requests", return_value=FAKE_PRS), patch(
        "app.ingest.fetch_pull_request_detail", return_value=FAKE_DETAIL
    ), patch("app.ingest.fetch_reviews", return_value=FAKE_REVIEWS):
        run_repository_sync(session, repo.id, token=None)

    session.refresh(repo)
    assert repo.status == "ready"
    assert repo.last_synced_at is not None

def test_run_repository_sync_marks_repo_error_on_failure(session):
    repo = _make_repo(session)
    with patch("app.ingest.fetch_pull_requests", side_effect=RuntimeError("GitHub API down")):
        run_repository_sync(session, repo.id, token=None)

    session.refresh(repo)
    assert repo.status == "error"
    assert repo.error_message == "GitHub API down"