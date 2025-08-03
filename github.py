# Github API interactions

import requests
from datetime import datetime, timezone


def get_recent_commit_time(username, repo):
    url = f"https://api.github.com/repos/{username}/{repo}/commits"
    try:
        response = requests.get(url)
        response.raise_for_status()
        commits = response.json()
        commit_time = commits[0]["commit"]["committer"]["date"]
        return datetime.strptime(commit_time, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=timezone.utc
        )
    except Exception:
        return None
