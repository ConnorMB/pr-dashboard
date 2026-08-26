from datetime import datetime, timezone

from app.models import PullRequest, Repository, Review


def test_repository_round_trip(session):
    repo = Repository(owner="octocat", name="hello", status="ready")
    session.add(repo)
    session.commit()

    fetched = session.query(Repository).filter_by(owner="octocat", name="hello").one()
    assert fetched.status == "ready"
    assert fetched.last_synced_at is None


def test_pull_request_round_trip(session):
    repo = Repository(owner="octocat", name="hello", status="ready")
    session.add(repo)
    session.commit()

    pr = PullRequest(
        repo_id=repo.id,
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

    fetched = session.query(PullRequest).filter_by(repo_id=repo.id, number=42).one()
    assert fetched.title == "Add feature X"
    assert fetched.additions == 120


def test_same_pr_number_allowed_across_different_repos(session):
    repo_a = Repository(owner="octocat", name="hello", status="ready")
    repo_b = Repository(owner="torvalds", name="linux", status="ready")
    session.add_all([repo_a, repo_b])
    session.commit()

    session.add(PullRequest(
        repo_id=repo_a.id, number=1, title="a", author="x",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    ))
    session.add(PullRequest(
        repo_id=repo_b.id, number=1, title="b", author="y",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    ))
    session.commit()

    assert session.query(PullRequest).count() == 2


def test_review_round_trip(session):
    repo = Repository(owner="octocat", name="hello", status="ready")
    session.add(repo)
    session.commit()

    pr = PullRequest(
        repo_id=repo.id, number=42, title="Add feature X", author="octocat",
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    session.add(pr)
    session.commit()

    review = Review(
        pull_request_id=pr.id,
        reviewer="hubot",
        state="APPROVED",
        submitted_at=datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    session.add(review)
    session.commit()

    fetched = session.query(Review).filter_by(pull_request_id=pr.id).one()
    assert fetched.reviewer == "hubot"
    assert fetched.state == "APPROVED"