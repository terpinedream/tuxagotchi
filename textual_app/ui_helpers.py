from datetime import timedelta
from typing import Optional
from textual_app.ascii_loader import ASCII_FRAMES


def load_ascii(mood: str, tick: int) -> str:
    frame_index = tick % 2
    return ASCII_FRAMES.get(mood, ["[Missing mood]"] * 2)[frame_index]


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


def generate_css(colors: dict) -> str:
    """
    Generate CSS string with colors from config.
    """
    return f"""
#main-container {{
    height: 100%;
    width: 100%;
    overflow: hidden;
    padding: 1 1 1 1;
}}

#root-container {{
    height: 100%;
    width: 100%;
}}

#tux-widget {{
    width: 60;
    padding: 1 2;
    margin: 1 0 0 0;
    border: round {colors["accent"]};
    background: {colors["background"]};
    color: {colors["foreground"]};
}}

#todo-widget {{
    min-width: 20;
    max-width: 20;
    padding: 1 2;
    margin: 1 0 0 0;
    border: none;
    background: transparent;
    color: {colors["foreground"]};
    overflow-y: auto;
}}

#cava-widget {{
    height: 2;
    width: 100%;
    padding: 1 2;
    margin: 1 0 0 0;
    border: round {colors["accent"]};
    background: {colors["background"]};
    color: {colors["foreground"]};
}}

#todo-input {{
    border: round white;
    background: transparent;
    color: {colors["foreground"]};
}}
"""
