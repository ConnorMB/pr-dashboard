from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.models import Repository

SYNC_CACHE_TTL = timedelta(hours=1)


def get_or_create_repository(
    session: Session, owner: str, name: str, now: datetime | None = None
) -> tuple[Repository, bool]:
    
    now = now or datetime.now(timezone.utc)

    repo = session.query(Repository).filter_by(owner=owner, name=name).one_or_none()
    if repo is None:
        repo = Repository(owner=owner, name=name, status="pending")
        session.add(repo)
        session.commit()
        return repo, True

    if repo.status == "syncing":
        return repo, False

    last_synced_at = repo.last_synced_at
    if last_synced_at is not None and last_synced_at.tzinfo is None:
        last_synced_at = last_synced_at.replace(tzinfo=timezone.utc)

    if last_synced_at is not None and now - last_synced_at < SYNC_CACHE_TTL:
        return repo, False

    return repo, True