import httpx

BASE_URL = "https://api.github.com"


def _headers(token: str | None) -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_pull_requests(owner: str, repo: str, token: str | None) -> list[dict]:
    results: list[dict] = []
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls"
    params = {"state": "all", "per_page": "100", "page": "1"}

    with httpx.Client(headers=_headers(token)) as client:
        while url:
            response = client.get(url, params=params)
            response.raise_for_status()
            for raw in response.json():
                results.append(
                    {
                        "number": raw["number"],
                        "title": raw["title"],
                        "author": raw["user"]["login"],
                        "created_at": raw["created_at"],
                        "merged_at": raw["merged_at"],
                        "closed_at": raw["closed_at"],
                    }
                )

            next_url = response.links.get("next", {}).get("url")
            url = next_url
            params = {}

    return results


def fetch_pull_request_detail(owner: str, repo: str, pr_number: int, token: str | None) -> dict:
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}"
    with httpx.Client(headers=_headers(token)) as client:
        response = client.get(url)
        response.raise_for_status()
        raw = response.json()
        return {
            "additions": raw["additions"],
            "deletions": raw["deletions"],
            "changed_files": raw["changed_files"],
        }


def fetch_reviews(owner: str, repo: str, pr_number: int, token: str | None) -> list[dict]:
    url = f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/reviews"
    with httpx.Client(headers=_headers(token)) as client:
        response = client.get(url)
        response.raise_for_status()
        return [
            {
                "reviewer": raw["user"]["login"],
                "state": raw["state"],
                "submitted_at": raw["submitted_at"],
            }
            for raw in response.json()
        ]
