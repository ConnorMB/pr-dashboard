from sqlalchemy.orm import Session

from app.models import PullRequest, Review


def time_to_merge_hours(session: Session) -> list[dict]:
    prs = session.query(PullRequest).filter(PullRequest.merged_at.isnot(None)).all()
    return [
        {
            "pr_number": pr.number,
            "hours": round((pr.merged_at - pr.created_at).total_seconds() / 3600, 2),
        }
        for pr in prs
    ]


def review_turnaround_hours(session: Session) -> list[dict]:
    prs = session.query(PullRequest).all()
    results = []
    for pr in prs:
        first_review = (
            session.query(Review)
            .filter(Review.pr_number == pr.number)
            .order_by(Review.submitted_at.asc())
            .first()
        )
        if first_review is None:
            continue
        hours = (first_review.submitted_at - pr.created_at).total_seconds() / 3600
        results.append({"pr_number": pr.number, "hours": round(hours, 2)})
    return results


def pr_size_distribution(session: Session) -> list[dict]:
    prs = session.query(PullRequest).all()
    return [
        {
            "pr_number": pr.number,
            "lines_changed": pr.additions + pr.deletions,
            "changed_files": pr.changed_files,
        }
        for pr in prs
    ]
