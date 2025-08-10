from pathlib import Path
from datetime import datetime, timedelta, timezone


class Tux:
    def __init__(self, username=None, repo=None):
        self.last_commit_time = None
        self.mood = "neutral"
        self.last_update_time = None
        # Animation frames by mood
        self.frame_index = 0
        self.frames_by_mood = {
            "happy": [],
            "neutral": [],
            "sad": [],
            "dead": [],
        }
        self.load_frames()

    def load_frames(self):
        assets_dir = Path(__file__).parent / "assets"
        for mood in ["happy", "neutral", "sad"]:
            for i in range(1, 3):
                frame_file = assets_dir / f"{mood}_{i}.txt"
                if frame_file.exists():
                    self.frames_by_mood[mood].append(frame_file.read_text())
                else:
                    self.frames_by_mood[mood].append(f"[Missing: {mood}_{i}.txt]")

    def get_current_frames(self):
        return self.frames_by_mood.get(self.mood, ["(?)", "(?)"])

    def get_frame(self):
        frames = self.get_current_frames()
        return frames[self.frame_index % len(frames)]

    def next_frame(self):
        self.frame_index += 1

    def update_mood(self, update_time=None):
        if update_time:
            self.last_update_time = update_time

        if self.last_update_time is None:
            self.mood = "neutral"
            return

        delta = datetime.now(timezone.utc) - self.last_update_time

        if delta < timedelta(hours=24):
            self.mood = "happy"
        elif delta < timedelta(days=2):
            self.mood = "neutral"
        elif delta < timedelta(days=7):
            self.mood = "sad"
        else:
            self.mood = "dead"

    def time_since_update(self):
        if self.last_update_time is None:
            return None
        return datetime.now(timezone.utc) - self.last_update_time

    def time_until_next_mood(self):
        delta = self.time_since_update()
        if delta is None:
            return None

        if self.mood == "happy":
            return timedelta(hours=24) - delta
        elif self.mood == "neutral":
            return timedelta(days=2) - delta
        elif self.mood == "sad":
            return timedelta(days=7) - delta
        else:
            return None

    def get_summary(self):
        return {
            "mood": self.mood,
            "since_update": self.time_since_update(),
            "next_mood_change": self.time_until_next_mood(),
        }
