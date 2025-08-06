from pathlib import Path
from datetime import datetime, timedelta, timezone
from github_api import get_recent_commits


class Tux:
    def __init__(self, username, repo):
        self.username = username
        self.repo = repo
        self.last_commit_time = None
        self.last_commit_data = []
        self.mood = "neutral"

        # Animation
        self.frame_index = 0
        self.frames_by_mood = {
            "happy": [],
            "neutral": [],
            "sad": [],
            "dead": [],  # Optional: you can add dead frames if desired
        }

        self.load_frames()

    def load_frames(self):
        assets_dir = Path(__file__).parent / "assets"
        for mood in ["happy", "neutral", "sad"]:
            for i in range(1, 3):  # frame_1.txt, frame_2.txt
                frame_file = assets_dir / f"{mood}_{i}.txt"
                if frame_file.exists():
                    self.frames_by_mood[mood].append(frame_file.read_text())
                else:
                    self.frames_by_mood[mood].append(f"[Missing: {mood}_{i}.txt]")

        # Optional: Dead mood default frame
        # self.frames_by_mood["dead"] = ["(×_×)", "(RIP)"]

    def get_current_frames(self):
        return self.frames_by_mood.get(self.mood, ["(?)", "(?)"])

    def get_frame(self):
        frames = self.get_current_frames()
        return frames[self.frame_index % len(frames)]

    def next_frame(self):
        self.frame_index += 1

    def update_mood(self, commit_time=None):
        if commit_time:
            self.last_commit_time = commit_time

        if self.last_commit_time is None:
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
            commit_time_str = self.last_commit_data[0]["commit"]["committer"]["date"]
            commit_time_dt = datetime.strptime(
                commit_time_str, "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=timezone.utc)
            self.last_commit_time = commit_time_dt
            self.update_mood(commit_time_dt)

    def time_since_commit(self):
        if self.last_commit_time is None:
            return None
        return datetime.now(timezone.utc) - self.last_commit_time

    def time_until_next_mood(self):
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

        now = datetime.utcnow()
        count_24h = 0
        count_7d = 0

        for commit in self.last_commit_data:
            commit_time = datetime.strptime(
                commit["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
            )
            delta = now - commit_time
            if delta.total_seconds() < 86400:
                count_24h += 1
            if delta.total_seconds() < 604800:
                count_7d += 1

        return {"24h": count_24h, "7d": count_7d}

    def get_summary(self):
        return {
            "mood": self.mood,
            "since_commit": self.time_since_commit(),
            "next_mood_change": self.time_until_next_mood(),
            "commit_counts": self.get_commit_counts(),
        }
