import httpx
import respx

from app.github_client import fetch_pull_requests, fetch_reviews


@respx.mock
def test_fetch_pull_requests_single_page():
    route = respx.get("https://api.github.com/repos/octocat/hello/pulls").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "number": 1,
                    "title": "Fix bug",
                    "user": {"login": "octocat"},
                    "created_at": "2026-01-01T00:00:00Z",
                    "merged_at": "2026-01-02T00:00:00Z",
                    "closed_at": "2026-01-02T00:00:00Z",
                    "additions": 10,
                    "deletions": 2,
                    "changed_files": 1,
                }
            ],
        )
    )

    prs = fetch_pull_requests("octocat", "hello", token=None)

    assert route.called
    assert len(prs) == 1
    assert prs[0]["number"] == 1
    assert prs[0]["author"] == "octocat"


@respx.mock
def test_fetch_pull_requests_follows_pagination():
    page1 = respx.get(
        "https://api.github.com/repos/octocat/hello/pulls",
        params={"state": "all", "per_page": "100", "page": "1"},
    ).mock(
        return_value=httpx.Response(
            200,
            json=[{"number": i, "title": "t", "user": {"login": "a"},
                    "created_at": "2026-01-01T00:00:00Z", "merged_at": None,
                    "closed_at": None, "additions": 0, "deletions": 0,
                    "changed_files": 0} for i in range(1, 101)],
            headers={"Link": '<https://api.github.com/repos/octocat/hello/pulls?state=all&per_page=100&page=2>; rel="next"'},
        )
    )
    page2 = respx.get(
        "https://api.github.com/repos/octocat/hello/pulls",
        params={"state": "all", "per_page": "100", "page": "2"},
    ).mock(
        return_value=httpx.Response(
            200,
            json=[{"number": 101, "title": "t", "user": {"login": "a"},
                    "created_at": "2026-01-01T00:00:00Z", "merged_at": None,
                    "closed_at": None, "additions": 0, "deletions": 0,
                    "changed_files": 0}],
        )
    )

    prs = fetch_pull_requests("octocat", "hello", token=None)

    assert page1.called and page2.called
    assert len(prs) == 101


@respx.mock
def test_fetch_reviews():
    respx.get("https://api.github.com/repos/octocat/hello/pulls/1/reviews").mock(
        return_value=httpx.Response(
            200,
            json=[
                {
                    "user": {"login": "hubot"},
                    "state": "APPROVED",
                    "submitted_at": "2026-01-02T00:00:00Z",
                }
            ],
        )
    )

    reviews = fetch_reviews("octocat", "hello", 1, token=None)

    assert len(reviews) == 1
    assert reviews[0]["reviewer"] == "hubot"
    assert reviews[0]["state"] == "APPROVED"
