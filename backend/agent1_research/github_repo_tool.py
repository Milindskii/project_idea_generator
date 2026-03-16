import requests

GITHUB_API = "https://api.github.com/search/repositories"


def search_github_repos(query: str, max_results: int = 10):
    """
    Search GitHub repositories for the given query.

    This helper is intentionally defensive so that a transient GitHub error
    does not break the whole multi-agent pipeline. On any error it returns
    an empty list and logs a short warning.
    """
    params = {
        "q": f"{query} in:name,description",
        "sort": "stars",
        "order": "desc",
        "per_page": max_results,
    }

    try:
        response = requests.get(GITHUB_API, params=params, timeout=30)
        response.raise_for_status()
        data = response.json() or {}
    except Exception as exc:
        print(f"[WARN] GitHub repo search failed: {exc}")
        return []

    items = data.get("items") or []
    repos = []

    for repo in items:
        repos.append(
            {
                "name": repo.get("name", ""),
                "description": repo.get("description") or "",
                "stars": repo.get("stargazers_count", 0),
                "language": repo.get("language"),
                "url": repo.get("html_url", ""),
            }
        )

    return repos