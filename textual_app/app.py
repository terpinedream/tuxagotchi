from datetime import datetime, timezone, timedelta
import asyncio
import os

from github_api import get_recent_commit_time
from textual.app import App
from textual.containers import Horizontal
from textual import log

from .tux import Tux
from .tux_widget import TuxWidget
from textual_app.todo_widget import TodoWidget
from config import load_config
from textual_app.ui_helpers import generate_css


class TuxApp(App):
    """Main Tuxagotchi Textual App"""

    BINDINGS = [("q", "quit", "Quit")]

    CSS_PATH = "styles.css"

    async def on_mount(self) -> None:
        # Load user config including colors
        config = load_config()
        self.username = config["github"]["username"]
        self.repo = config["github"]["repo"]
        self.theme_colors = config["colors"]

        # GitHub commit tracking
        self.last_valid_commit_time = None
        self.last_checked = datetime.min.replace(tzinfo=timezone.utc)

        # Initialize Tux logic and UI
        self.tux = Tux(username=self.username, repo=self.repo)
        self.tux_widget = TuxWidget(self.tux, self.repo, id="tux-widget")
        self._style_tux_widget()

        # Initialize Todo UI
        self.todo_widget = TodoWidget(id="todo-widget")
        self._style_todo_widget()
        self._style_todo_widget()

        # Layout container
        container = Horizontal(self.tux_widget, self.todo_widget, id="main-container")
        container.styles.height = "100%"
        container.styles.width = "100%"
        container.styles.overflow = "hidden"

        await self.mount(container)
        self.set_interval(60, self.check_github)

    def _style_tux_widget(self) -> None:
        self.tux_widget.styles.flex = 0
        self.tux_widget.styles.padding = (1, 2)
        self.tux_widget.styles.height = "auto"
        self.tux_widget.styles.width = "auto"
        self.tux_widget.styles.margin = (1, 0, 0, 0)

    def _style_todo_widget(self) -> None:
        self.todo_widget.styles.flex = 1
        self.todo_widget.styles.width = 40
        self.todo_widget.styles.max_width = 50
        self.todo_widget.styles.padding = (1, 2)
        self.todo_widget.styles.margin = (1, 0, 0, 0)

    async def check_github(self) -> None:
        now = datetime.now(timezone.utc)
        if now - self.last_checked < timedelta(seconds=60):
            return
        self.last_checked = now

        commit_time = await asyncio.to_thread(
            get_recent_commit_time, self.username, self.repo
        )

        if commit_time:
            self.last_valid_commit_time = commit_time
            self.tux.last_commit_time = commit_time
            self.tux.update_mood(commit_time)
            log(f"[✓] Fetched new commit time: {commit_time}")
        elif not self.last_valid_commit_time:
            log("[!] No commit found, and no fallback yet.")

        self.tux_widget.refresh()


def generate_css_file():
    css_path = "textual_app/styles.css"
    if not os.path.exists(css_path):
        config = load_config()
        colors = config["colors"]
        css = generate_css(colors)
        with open(css_path, "w") as f:
            f.write(css)


if __name__ == "__main__":
    generate_css_file()
    app = TuxApp()
    app.run()
