from textual.timer import Timer
from textual.widget import Widget
from textual.reactive import reactive
from rich.panel import Panel
from rich.text import Text
from rich import box
from datetime import datetime

# Import UI helper functions from ui_helpers
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
        self.last_update_time = None
        self.tick = 0
        self._timer: Timer | None = None

    def on_mount(self):
        self._timer = self.set_interval(2, self.increment_tick)

    def increment_tick(self):
        self.tick += 1
        self.refresh()

    def render(self) -> Panel:
        art = center_ascii(load_ascii(self.tux.mood, self.tick))
        last_update_td = self.tux.time_since_update()
        countdown_td = self.tux.time_until_next_mood()

        print(
            f"[DEBUG] Mood: {self.tux.mood}, Countdown: {countdown_td}"
        )  # Debug print

        last_update_text = "Thinking..."
        if last_update_td:
            last_update_text = f"{format_timedelta(last_update_td)} ago"

        tux_lines = [
            art,
            "",
            f"[bold]Mood:[/bold] {self.tux.mood.upper()}",
            f"[bold]Last Update:[/bold] {last_update_text}",
        ]

        if countdown_td:
            hunger_bar = generate_block_bar(self.tux, self.tick, length=10)
            print(f"[DEBUG] Hunger bar: {hunger_bar}")  # Debug print
            tux_lines.append(
                f"[bold]Hungry in:[/bold] {format_timedelta(countdown_td)} {hunger_bar}"
            )

        return Panel.fit(
            Text.from_markup("\n".join(tux_lines)),
            title="Tuxagotchi",
            width=60,
            box=box.ROUNDED,
        )
