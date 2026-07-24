from unittest.mock import patch

from app.ingest import sync_repository
from app.models import PullRequest, Review


FAKE_PRS = [
    {
        "number": 1,
        "title": "Fix bug",
        "author": "octocat",
        "created_at": "2026-01-01T00:00:00Z",
        "merged_at": "2026-01-02T00:00:00Z",
        "closed_at": "2026-01-02T00:00:00Z",
        "additions": 10,
        "deletions": 2,
        "changed_files": 1,
    }
]

FAKE_REVIEWS = [
    {"reviewer": "hubot", "state": "APPROVED", "submitted_at": "2026-01-01T12:00:00Z"}
]


def test_sync_repository_inserts_prs_and_reviews(session):
    with patch("app.ingest.fetch_pull_requests", return_value=FAKE_PRS), patch(
        "app.ingest.fetch_reviews", return_value=FAKE_REVIEWS
    ):
        result = sync_repository(session, "octocat", "hello", token=None)

    assert result == {"pull_requests": 1, "reviews": 1}
    assert session.query(PullRequest).count() == 1
    assert session.query(Review).count() == 1


def test_sync_repository_is_idempotent(session):
    with patch("app.ingest.fetch_pull_requests", return_value=FAKE_PRS), patch(
        "app.ingest.fetch_reviews", return_value=FAKE_REVIEWS
    ):
        sync_repository(session, "octocat", "hello", token=None)
        sync_repository(session, "octocat", "hello", token=None)

    assert session.query(PullRequest).count() == 1
    assert session.query(Review).count() == 1
