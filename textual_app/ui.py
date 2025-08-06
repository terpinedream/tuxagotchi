from typing import Optional
from datetime import timedelta
import os
from textual.widgets import Static


def load_ascii(mood: str, tick: int) -> str:
    base_path = f"assets/{mood}.txt"
    alt_path = f"assets/{mood}2.txt"

    try:
        with open(base_path) as f:
            base_lines = f.readlines()
    except FileNotFoundError:
        base_lines = ["(?)\n"]

    try:
        with open(alt_path) as f:
            alt_lines = f.readlines()
    except FileNotFoundError:
        alt_lines = base_lines

    max_height = max(len(base_lines), len(alt_lines))
    base_lines += ["\n"] * (max_height - len(base_lines))
    alt_lines += ["\n"] * (max_height - len(alt_lines))

    return "".join(base_lines if tick % 2 == 0 else alt_lines)


tux_style = "bold white"


def format_timedelta(td: timedelta) -> str:
    seconds = int(td.total_seconds())
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    else:
        return f"{seconds // 86400}d"


class CustomStyles:
    tux_style = None
    todo_style = None


def generate_block_bar(tux: object, tick: int, length: int = 10) -> str:
    """
    Generate a block progress bar indicating time until next mood change.
    `tux` must have `time_until_next_mood()` and `mood` attributes.
    """
    countdown = tux.time_until_next_mood()
    if not countdown:
        return ""  # No countdown for sad/dead moods

    if tux.mood == "happy":
        total = 4 * 3600  # 4 hours
    elif tux.mood == "neutral":
        total = 24 * 3600  # 1 day
    else:
        return ""

    remaining = countdown.total_seconds()
    progress = remaining / total
    blocks_filled = int(progress * length)
    blocks_empty = length - blocks_filled

    animation = ["░", "▒", "▓", "█", "▓", "▒"]
    frame = animation[tick % len(animation)]

    if blocks_filled > 0:
        return "█" * (blocks_filled - 1) + frame + "░" * blocks_empty
    else:
        return frame + "░" * (length - 1)


def center_ascii(art: str, width: int = 32) -> str:
    lines = art.splitlines()
    return "\n".join(line.center(width) for line in lines)
