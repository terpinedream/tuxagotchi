# Github API interactions

import requests
from datetime import datetime, timezone


def get_recent_commits(username, repo, per_page=30):
    """
    Fetches the latest commits for a repo. Returns a list of commit data.
    """
    url = f"https://api.github.com/repos/{username}/{repo}/commits"
    params = {"per_page": per_page}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[DEBUG] Failed to fetch commits: {e}")
        return []


def get_recent_commit_time(username, repo):
    commits = get_recent_commits(username, repo)
    if commits:
        commit_time = commits[0]["commit"]["committer"]["date"]
        return datetime.strptime(commit_time, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    return None
