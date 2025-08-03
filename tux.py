from datetime import datetime, timedelta, timezone


class Tux:
    def __init__(self, username, repo):
        self.username = username
        self.repo = repo
        self.last_commit_time = None
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
