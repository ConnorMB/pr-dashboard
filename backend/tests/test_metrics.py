from datetime import datetime, timezone

from app.metrics import (
    pr_size_distribution,
    review_turnaround_hours,
    time_to_merge_hours,
)
from app.models import PullRequest, Review


def _dt(*args):
    return datetime(*args, tzinfo=timezone.utc)


def test_time_to_merge_hours(session):
    session.add(
        PullRequest(
            number=1, title="a", author="x",
            created_at=_dt(2026, 1, 1, 0, 0),
            merged_at=_dt(2026, 1, 1, 12, 0),
        )
    )
    session.add(
        PullRequest(
            number=2, title="b", author="x",
            created_at=_dt(2026, 1, 1, 0, 0),
            merged_at=None,  # not merged, excluded
        )
    )
    session.commit()

    result = time_to_merge_hours(session)

    assert result == [{"pr_number": 1, "hours": 12.0}]


def test_review_turnaround_hours(session):
    session.add(
        PullRequest(number=1, title="a", author="x", created_at=_dt(2026, 1, 1, 0, 0))
    )
    session.add(
        Review(pr_number=1, reviewer="r1", state="APPROVED", submitted_at=_dt(2026, 1, 1, 6, 0))
    )
    session.add(
        Review(pr_number=1, reviewer="r2", state="APPROVED", submitted_at=_dt(2026, 1, 1, 9, 0))
    )
    session.commit()

    result = review_turnaround_hours(session)

    assert result == [{"pr_number": 1, "hours": 6.0}]  # time to FIRST review


def test_pr_size_distribution(session):
    session.add(
        PullRequest(
            number=1, title="a", author="x", created_at=_dt(2026, 1, 1),
            additions=100, deletions=20, changed_files=3,
        )
    )
    session.commit()

    result = pr_size_distribution(session)

    assert result == [{"pr_number": 1, "lines_changed": 120, "changed_files": 3}]
