from sqlalchemy.orm import Session
from app.models import PullRequest, Review
from datetime import datetime, timezone


def time_to_merge_hours(session: Session, repo_id: int) -> list[dict]:
    prs = (
        session.query(PullRequest)
        .filter(PullRequest.merged_at.isnot(None), PullRequest.repo_id == repo_id)
        .all()
    )
    return [
        {
            "pr_number": pr.number,
            "hours": round((pr.merged_at - pr.created_at).total_seconds() / 3600, 2),
        }
        for pr in prs
    ]


def review_turnaround_hours(session: Session, repo_id: int) -> list[dict]:
    prs = session.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()
    results = []
    for pr in prs:
        first_review = (
            session.query(Review)
            .filter(Review.pull_request_id == pr.id)
            .order_by(Review.submitted_at.asc())
            .first()
        )
        if first_review is None:
            continue
        hours = (first_review.submitted_at - pr.created_at).total_seconds() / 3600
        results.append({"pr_number": pr.number, "hours": round(hours, 2)})
    return results


def pr_size_distribution(session: Session, repo_id: int) -> list[dict]:
    prs = (
        session.query(PullRequest)
        .filter(PullRequest.repo_id == repo_id)
        .all()
    )
    return [
        {
            "pr_number": pr.number,
            "lines_changed": pr.additions + pr.deletions,
            "changed_files": pr.changed_files,
        }
        for pr in prs
    ]

def stale_open_prs(session: Session, repo_id: int, now: datetime, min_inactive_days: int = 14) -> list[dict]:
    open_prs = (
        session.query(PullRequest)
        .filter(
            PullRequest.repo_id == repo_id,
            PullRequest.merged_at.is_(None),
            PullRequest.closed_at.is_(None),
        )
        .all()
    )

    def _last_activity(pr: PullRequest) -> datetime:
        last_activity = pr.updated_at if pr.updated_at else pr.created_at
        if last_activity.tzinfo is None:
            last_activity = last_activity.replace(tzinfo=timezone.utc)
        return last_activity

    def _days_inactive(pr: PullRequest) -> int:
        return (now - _last_activity(pr)).days

    stale = [
        {
            "pr_number": pr.number,
            "title": pr.title,
            "author": pr.author,
            "days_inactive": _days_inactive(pr),
        }
        for pr in open_prs
        if _days_inactive(pr) >= min_inactive_days
    ]
    return sorted(stale, key=lambda item: item["days_inactive"], reverse=True)


