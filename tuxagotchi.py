import time
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

sys.path.append(str(Path(__file__).resolve().parent))

from github import get_recent_commit_time
from tux import Tux
from ui import render
import tomllib


def load_config():
    with open("config.toml", "rb") as f:
        return tomllib.load(f)


def main():
    config = load_config()
    username = config["github"]["username"]
    repo = config["github"]["repo"]
    tux = Tux(username=username, repo=repo)

    last_valid_commit_time = None
    tick = 0
    last_checked = datetime.min.replace(tzinfo=timezone.utc)
    CHECK_INTERVAL = timedelta(seconds=60)

    while True:
        now = datetime.now(timezone.utc)
        if now - last_checked >= CHECK_INTERVAL:
            commit_time = get_recent_commit_time(username, repo)
            last_checked = now

            if commit_time:
                last_valid_commit_time = commit_time
                tux.last_commit_time = commit_time
                print(f"[✓] Fetched new commit time: {commit_time}")
            elif not last_valid_commit_time:
                print("[!] No commit found, and no fallback yet.")
            # tux.mood = "happy"
            tux.update_mood(last_valid_commit_time)
        render(tux, repo_name=repo, tick=tick)
        tick += 1
        time.sleep(1)


if __name__ == "__main__":
    main()
