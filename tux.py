from datetime import datetime, timedelta, timezone
from github import get_recent_commits


class Tux:
    def __init__(self, username, repo):
        self.username = username
        self.repo = repo
        self.last_commit_time = None
        self.last_commit_data = []
        self.mood = "neutral"

    def update_mood(self, commit_time=None):
        # Only update last_commit_time if we actually got a valid one
        if commit_time:
            self.last_commit_time = commit_time

        if self.last_commit_time is None:
            # No valid commit time yet — assume neutral as safe default
            self.mood = "neutral"
            return

        delta = datetime.now(timezone.utc) - self.last_commit_time

        if delta < timedelta(hours=4):
            self.mood = "happy"
        elif delta < timedelta(days=1):
            self.mood = "neutral"
        elif delta < timedelta(days=2):
            self.mood = "sad"
        else:
            self.mood = "dead"

    def fetch_commits(self):
        self.last_commit_data = get_recent_commits(self.username, self.repo)
        if self.last_commit_data:
            commit_time = self.last_commit_data[0]["commit"]["committer"]["date"]
            self.last_commit_time = datetime.strptime(
                commit_time, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)

    def time_since_commit(self):
        if self.last_commit_time is None:
            return None
        delta = datetime.now(timezone.utc) - self.last_commit_time
        return delta

    def time_until_next_mood(self):
        if self.last_commit_time is None:
            return None

        delta = self.time_since_commit()
        if delta is None:
            return None

        if self.mood == "happy":
            return timedelta(hours=4) - delta
        elif self.mood == "neutral":
            return timedelta(days=1) - delta
        elif self.mood == "sad":
            return timedelta(days=2) - delta
        else:
            return None

    def get_commit_counts(self):
        if not self.last_commit_data:
            return {"24h": 0, "7d": 0}

        now = datetime.datetime.utcnow()
        count_24h = 0
        count_7d = 0

        for commit in self.last_commit_data.get("commits", []):
            commit_time = datetime.datetime.strptime(
                commit["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
            )
            delta = now - commit_time
            if delta.total_seconds() < 86400:
                count_24h += 1
            if delta.total_seconds() < 604800:
                count_7d += 1

        return {"24h": count_24h, "7d": count_7d}
