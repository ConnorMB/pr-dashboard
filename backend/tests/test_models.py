from datetime import datetime, timezone

from app.models import PullRequest, Review


def test_pull_request_round_trip(session):
    pr = PullRequest(
        number=42,
        title="Add feature X",
        author="octocat",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        merged_at=datetime(2026, 1, 3, tzinfo=timezone.utc),
        closed_at=None,
        additions=120,
        deletions=15,
        changed_files=4,
    )
    session.add(pr)
    session.commit()

    fetched = session.query(PullRequest).filter_by(number=42).one()
    assert fetched.title == "Add feature X"
    assert fetched.additions == 120


def test_review_round_trip(session):
    pr = PullRequest(
        number=42,
        title="Add feature X",
        author="octocat",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    session.add(pr)
    session.commit()

    review = Review(
        pr_number=42,
        reviewer="hubot",
        state="APPROVED",
        submitted_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    session.add(review)
    session.commit()

    fetched = session.query(Review).filter_by(pr_number=42).one()
    assert fetched.reviewer == "hubot"
    assert fetched.state == "APPROVED"
