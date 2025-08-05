# ui.py
from rich.columns import Columns
from datetime import datetime
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
        with open(base_path, encoding="utf-8") as f:
            base_lines = f.readlines()
    except FileNotFoundError:
        base_lines = ["(?)\n"]

    try:
        with open(alt_path, encoding="utf-8") as f:
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
    sys.stdout.write("\033c")
    sys.stdout.flush()

    # ASCII art + info
    art = load_ascii(tux.mood, tick)
    last_commit_td = tux.time_since_commit()
    countdown_td = tux.time_until_next_mood()

    last_commit_text = "Unknown"
    if last_commit_td:
        last_commit_text = f"{format_timedelta(last_commit_td)} ago"

    # Time string
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Tux panel
    tux_lines = [
        art,
        "",
        f"[bold]Mood:[/bold] {tux.mood.upper()}",
        f"[bold]Repo:[/bold] {repo_name}",
        f"[bold]Last Commit:[/bold] {last_commit_text}",
    ]

    if countdown_td:
        hunger_bar = generate_block_bar(tux, tick=tick, length=10)
        tux_lines.append(
            f"[bold]Hungry in:[/bold] {format_timedelta(countdown_td)} {hunger_bar}"
        )

    while len(tux_lines) < 5:
        tux_lines.append("")

    tux_panel = Panel.fit(
        Text.from_markup("\n".join(tux_lines)),
        title="Tuxagotchi",
        width=62,
        box=box.ROUNDED,
    )

    commit_counts = tux.get_commit_counts()

    stats_lines = [
        "[bold]Stats[/bold]",
        f" Commits (24h): {commit_counts['24h']}",
        f" Commits (7d): {commit_counts['7d']}",
        "",
        f" Time: {now}",
    ]

    stats_body = "\n".join(stats_lines)

    stats_panel = Panel.fit(
        Text.from_markup(stats_body),
        title="Stats",
        width=30,
        box=box.ROUNDED,
    )

    console.print(Columns([tux_panel, stats_panel]))
