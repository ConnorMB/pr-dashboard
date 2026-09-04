from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.github_client import fetch_pull_request_detail, fetch_pull_requests, fetch_reviews
from app.models import PullRequest, Review, Repository

MAX_PRS_PER_SYNC = 200

def _parse(ts: str | None) -> datetime | None:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None


def sync_repository(session: Session,repo_id: int, owner: str, name: str, token: str | None) -> dict:
    raw_prs = fetch_pull_requests(owner, name, token,max_results=MAX_PRS_PER_SYNC)
    pr_count = 0
    review_count = 0

    for raw in raw_prs:
        existing = session.query(PullRequest).filter_by(repo_id=repo_id,number=raw["number"]).one_or_none()
        if existing is None:
            existing = PullRequest(repo_id=repo_id, number=raw["number"])
            session.add(existing)
            

        detail = fetch_pull_request_detail(owner, name, raw["number"], token)

        existing.title = raw["title"]
        existing.author = raw["author"]
        existing.created_at = _parse(raw["created_at"])
        existing.merged_at = _parse(raw["merged_at"])
        existing.closed_at = _parse(raw["closed_at"])
        existing.additions = detail["additions"]
        existing.deletions = detail["deletions"]
        existing.changed_files = detail["changed_files"]
        pr_count += 1

        session.flush()

        session.query(Review).filter_by(pull_request_id=existing.id).delete()
        for raw_review in fetch_reviews(owner, name, raw["number"], token):
            session.add(
                Review(
                    pull_request_id=existing.id,
                    reviewer=raw_review["reviewer"],
                    state=raw_review["state"],
                    submitted_at=_parse(raw_review["submitted_at"]),
                )
            )
            review_count += 1

    session.commit()
    return {"pull_requests": pr_count, "reviews": review_count}

def run_repository_sync(session: Session, repo_id: int, token: str | None) -> None:
    repo = session.query(Repository).filter_by(id=repo_id).one()
    repo.status = "syncing"
    repo.error_message = None
    session.commit()

    try:
        sync_repository(session, repo.id, repo.owner, repo.name, token)
    except Exception as exc:
        repo.status = "error"
        repo.error_message = str(exc)
        session.commit()
        return

    repo.status = "ready"
    repo.last_synced_at = datetime.now(timezone.utc)
    session.commit()