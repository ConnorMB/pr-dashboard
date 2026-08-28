from datetime import datetime, timezone

from app.metrics import pr_size_distribution,review_turnaround_hours,time_to_merge_hours
from app.models import PullRequest, Review, Repository


def _dt(*args):
    return datetime(*args, tzinfo=timezone.utc)

def _make_repo(session, owner="octocat", name="hello"):
    repo = Repository(owner=owner, name=name, status="ready")
    session.add(repo)
    session.commit()
    return repo

def test_time_to_merge_hours(session):
    repo = _make_repo(session)
    session.add(
        PullRequest(
            repo_id=repo.id,number=1, title="a", author="x",
            created_at=_dt(2026, 1, 1, 0, 0),
            merged_at=_dt(2026, 1, 1, 12, 0),
        )
    )
    session.add(
        PullRequest(
            repo_id=repo.id,number=2, title="b", author="x",
            created_at=_dt(2026, 1, 1, 0, 0),
            merged_at=None,  # not merged, excluded
        )
    )
    session.commit()

    result = time_to_merge_hours(session, repo.id)

    assert result == [{"pr_number": 1, "hours": 12.0}]


def test_review_turnaround_hours(session):
    repo = _make_repo(session)
    pr = PullRequest(repo_id=repo.id, number=1, title="a", author="x", created_at=_dt(2026, 1, 1, 0, 0))
    session.add(pr)
    session.commit()

    session.add(Review(pull_request_id=pr.id, reviewer="r1", state="APPROVED", submitted_at=_dt(2026, 1, 1, 6, 0)))
    session.add(Review(pull_request_id=pr.id, reviewer="r2", state="APPROVED", submitted_at=_dt(2026, 1, 1, 9, 0)))
    
    session.commit()

    result = review_turnaround_hours(session, repo.id)

    assert result == [{"pr_number": 1, "hours": 6.0}]  # time to first review


def test_pr_size_distribution(session):
    repo = _make_repo(session)
    session.add(
        PullRequest(
            repo_id=repo.id, number=1, title="a", author="x", created_at=_dt(2026, 1, 1),
            additions=100, deletions=20, changed_files=3,
        )
    )
    session.commit()

    result = pr_size_distribution(session, repo.id)

    assert result == [{"pr_number": 1, "lines_changed": 120, "changed_files": 3}]

def test_time_to_merge_hours_only_includes_the_given_repo(session):
    repo_a = _make_repo(session, "octocat", "hello")
    repo_b = _make_repo(session, "torvalds", "linux")
    session.add(PullRequest(
        repo_id=repo_a.id, number=1, title="a", author="x",
        created_at=_dt(2026, 1, 1, 0, 0), merged_at=_dt(2026, 1, 1, 12, 0),
    ))
    session.add(PullRequest(
        repo_id=repo_b.id, number=1, title="b", author="y",
        created_at=_dt(2026, 1, 1, 0, 0), merged_at=_dt(2026, 1, 1, 6, 0),
    ))
    session.commit()

    result = time_to_merge_hours(session, repo_a.id)

    assert result == [{"pr_number": 1, "hours": 12.0}]