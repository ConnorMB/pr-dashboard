from datetime import datetime, timezone

from app.models import Repository
from app.repositories import get_or_create_repository


def _dt(*args):
    return datetime(*args, tzinfo=timezone.utc)


def test_creates_new_repository_and_requests_sync(session):
    repo, needs_sync = get_or_create_repository(session, "octocat", "hello", now=_dt(2026, 1, 1))

    assert needs_sync is True
    assert repo.owner == "octocat"
    assert repo.status == "pending"
    assert session.query(Repository).count() == 1


def test_returns_existing_repository_without_sync_when_recently_synced(session):
    session.add(Repository(
        owner="octocat", name="hello", status="ready",
        last_synced_at=_dt(2026, 1, 1, 0, 0),
    ))
    session.commit()

    repo, needs_sync = get_or_create_repository(session, "octocat", "hello", now=_dt(2026, 1, 1, 0, 30))

    assert needs_sync is False
    assert repo.status == "ready"


def test_requests_resync_when_cache_ttl_expired(session):
    session.add(Repository(
        owner="octocat", name="hello", status="ready",
        last_synced_at=_dt(2026, 1, 1, 0, 0),
    ))
    session.commit()

    repo, needs_sync = get_or_create_repository(session, "octocat", "hello", now=_dt(2026, 1, 1, 2, 0))

    assert needs_sync is True


def test_does_not_requeue_a_sync_already_in_progress(session):
    session.add(Repository(owner="octocat", name="hello", status="syncing"))
    session.commit()

    repo, needs_sync = get_or_create_repository(session, "octocat", "hello", now=_dt(2026, 1, 1))

    assert needs_sync is False
    assert repo.status == "syncing"