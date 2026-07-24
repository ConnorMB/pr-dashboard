from datetime import datetime

from sqlalchemy.orm import Session

from app.github_client import fetch_pull_requests, fetch_reviews
from app.models import PullRequest, Review


def _parse(ts: str | None) -> datetime | None:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")) if ts else None


def sync_repository(session: Session, owner: str, repo: str, token: str | None) -> dict:
    raw_prs = fetch_pull_requests(owner, repo, token)
    pr_count = 0
    review_count = 0

    for raw in raw_prs:
        existing = session.query(PullRequest).filter_by(number=raw["number"]).one_or_none()
        if existing is None:
            existing = PullRequest(number=raw["number"])
            session.add(existing)

        existing.title = raw["title"]
        existing.author = raw["author"]
        existing.created_at = _parse(raw["created_at"])
        existing.merged_at = _parse(raw["merged_at"])
        existing.closed_at = _parse(raw["closed_at"])
        existing.additions = raw["additions"]
        existing.deletions = raw["deletions"]
        existing.changed_files = raw["changed_files"]
        pr_count += 1

        session.query(Review).filter_by(pr_number=raw["number"]).delete()
        for raw_review in fetch_reviews(owner, repo, raw["number"], token):
            session.add(
                Review(
                    pr_number=raw["number"],
                    reviewer=raw_review["reviewer"],
                    state=raw_review["state"],
                    submitted_at=_parse(raw_review["submitted_at"]),
                )
            )
            review_count += 1

    session.commit()
    return {"pull_requests": pr_count, "reviews": review_count}
