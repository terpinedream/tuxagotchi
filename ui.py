# ui.py

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import sys
import os

console = Console()


def load_ascii(mood, tick):
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

    # Ensure same height by padding whichever is shorter
    max_height = max(len(base_lines), len(alt_lines))
    base_lines += ["\n"] * (max_height - len(base_lines))
    alt_lines += ["\n"] * (max_height - len(alt_lines))

    return "".join(base_lines if tick % 2 == 0 else alt_lines)


def format_timedelta(td):
    seconds = int(td.total_seconds())
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    else:
        return f"{seconds // 86400}d"


def generate_block_bar(tux, tick, length=10):
    countdown = tux.time_until_next_mood()
    if not countdown:
        return ""  # No countdown for sad/dead

    # Total time per mood stage
    if tux.mood == "happy":
        total = 4 * 3600  # 4 hours
    elif tux.mood == "neutral":
        total = 24 * 3600  # 1 day
    else:
        return ""

    remaining = countdown.total_seconds()
    progress = remaining / total  # Now: 1.0 when full, 0.0 when empty
    blocks_filled = int(progress * length)
    blocks_empty = length - blocks_filled

    # Animate the last filled block to "bounce"
    animation = ["░", "▒", "▓", "█", "▓", "▒"]
    frame = animation[tick % len(animation)]

    if blocks_filled > 0:
        return "█" * (blocks_filled - 1) + frame + "░" * blocks_empty
    else:
        return frame + "░" * (length - 1)


def center_ascii(art, width=32):
    lines = art.splitlines()
    return "\n".join(line.center(width) for line in lines)


def render(tux, repo_name, tick):
    sys.stdout.write("\033c")  # Clear the terminal
    sys.stdout.flush()

    # ASCII art with animation
    art = load_ascii(tux.mood, tick)

    # Build metadata text
    last_commit_td = tux.time_since_commit()
    countdown_td = tux.time_until_next_mood()

    last_commit_text = "Unknown"
    if last_commit_td:
        last_commit_text = f"{format_timedelta(last_commit_td)} ago"

    lines = [
        art,
        "",
        f"[bold]Mood:[/bold] {tux.mood.upper()}",
        f"[bold]Repo:[/bold] {repo_name}",
        f"[bold]Last Commit:[/bold] {last_commit_text}",
    ]

    if countdown_td:
        hunger_bar = generate_block_bar(tux, tick=tick, length=10)
        lines.append(
            f"[bold]Hungry in:[/bold] {format_timedelta(countdown_td)} {hunger_bar}"
        )

    # Pad the lines to a minimum height
    # MIN_LINES = 20
    # while len(lines) < MIN_LINES:
    #     lines.append("")

    body = "\n".join(lines)

    panel = Panel.fit(
        Text.from_markup(body),
        title="Tuxagotchi",
        width=65,  # Set a fixed width — adjust if needed
        box=box.ROUNDED,  # You can use box=box.ROUNDED or box.SQUARE too
    )

    console.print(panel)
