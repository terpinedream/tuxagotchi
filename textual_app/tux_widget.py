from textual.timer import Timer
from textual.widget import Widget
from textual.reactive import reactive
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box
from datetime import datetime
from textual.widgets import Static
from textual_app.ui import CustomStyles
from textual_app.ui_helpers import (
    load_ascii,
    format_timedelta,
    generate_block_bar,
    center_ascii,
)


class TuxWidget(Widget):
    tick = reactive(0)

    def __init__(self, tux, repo_name: str):
        super().__init__()
        self.tux = tux
        self.repo_name = repo_name
        self.tick = 0
        self._timer: Timer | None = None

    def on_mount(self):
        # Set a timer to increment tick every 0.5 seconds
        self._timer = self.set_interval(2, self.increment_tick)

    def increment_tick(self):
        self.tick += 1
        self.refresh()

    def render(self) -> Panel:
        art = center_ascii(load_ascii(self.tux.mood, self.tick))
        last_commit_td = self.tux.time_since_commit()
        countdown_td = self.tux.time_until_next_mood()

        last_commit_text = "Unknown"
        if last_commit_td:
            last_commit_text = f"{format_timedelta(last_commit_td)} ago"

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        tux_lines = [
            art,
            "",
            f"[bold]Mood:[/bold] {self.tux.mood.upper()}",
            f"[bold]Repo:[/bold] {self.repo_name}",
            f"[bold]Committed:[/bold] {last_commit_text}",
        ]
        if countdown_td:
            hunger_bar = generate_block_bar(self.tux, self.tick, length=10)
            tux_lines.append(
                f"[bold]Hungry in:[/bold] {format_timedelta(countdown_td)} {hunger_bar}"
            )

        return Panel.fit(
            Text.from_markup("\n".join(tux_lines)),
            title="Tuxagotchi",
            width=60,
            box=box.ROUNDED,
        )
