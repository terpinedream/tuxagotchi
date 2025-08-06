from pathlib import Path

ASCII_FRAMES = {}


def preload_ascii_frames(asset_dir="assets"):
    moods = ["happy", "neutral", "sad"]
    for mood in moods:
        ASCII_FRAMES[mood] = []
        for i in range(2):
            path = Path(asset_dir) / f"{mood}_{i + 1}.txt"
            if path.exists():
                ASCII_FRAMES[mood].append(path.read_text())
            else:
                ASCII_FRAMES[mood].append(f"[Missing {mood}_{i + 1}]")
