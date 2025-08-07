from datetime import datetime, timezone, timedelta
import asyncio
import os
from github_api import get_recent_commit_time
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual import log
from textual_app.cava_widget import CavaWidget
from textual_app.tux import Tux
from textual_app.tux_widget import TuxWidget
from textual_app.todo_widget import TodoWidget
from config import load_config
from textual_app.ui_helpers import generate_css
from textual_app.ascii_loader import preload_ascii_frames
from textual.widgets import Static


class TuxApp(App):
    """Main Tuxagotchi Textual App"""

    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = "styles.css"

    async def on_mount(self) -> None:
        # Preload ascii for better proformance
        preload_ascii_frames()
        # Load user config including colors
        config = load_config()
        self.username = config["github"]["username"]
        self.repo = config["github"]["repo"]
        self.token = config["github"]["token"]
        self.theme_colors = config["colors"]

        # GitHub commit tracking
        self.last_valid_commit_time = None
        self.last_checked = datetime.min.replace(tzinfo=timezone.utc)

        # Initialize Tux logic and UI
        self.tux = Tux(username=self.username, repo=self.repo)
        self.tux_widget = TuxWidget(self.tux, self.repo)
        self._style_tux_widget()

        self.todo_widget = TodoWidget(id="todo-widget")
        self._style_todo_widget()

        # self.cava_widget = CavaWidget(id="cava-widget")
        # self._style_cava_widget()

        top_row = Horizontal(self.tux_widget, self.todo_widget, id="main-container")
        await self.mount(top_row)
        # await self.mount(self.cava_widget)

        # Keybinds bar
        self.keybinds = Static(
            "[bold][/bold]【q ➡ Quit】【a ➡ Insert】【x ➡ Delete】【j/k ➡ Up/Down】【esc ➡ Navigate】",
            id="keybinds",
        )
        self.keybinds.styles.dock = "bottom"
        self.keybinds.styles.height = 1
        self.keybinds.styles.background = "transparent"
        self.keybinds.styles.color = "white"
        self.keybinds.styles.padding = (0, 1)
        await self.mount(self.keybinds)

        # Reduced check interval from 60
        # Token implementation now increases rate limit to 5k/hr
        self.set_interval(30, self.check_github)

    def _style_tux_widget(self) -> None:
        # self.tux_widget.styles.flex = 1
        self.tux_widget.styles.padding = (0, 0)
        self.tux_widget.styles.height = 35
        self.tux_widget.styles.width = 50
        self.tux_widget.styles.margin = (0, 0, 0, 0)

    def _style_todo_widget(self) -> None:
        self.todo_widget.styles.width = 20
        self.todo_widget.styles.min_width = 20
        self.todo_widget.styles.max_width = 20
        self.todo_widget.styles.height = 35
        self.todo_widget.styles.max_height = 35
        self.todo_widget.styles.margin = (0, 0, 0, 0)
        self.todo_widget.styles.padding = (0, 0)

    # def _style_cava_widget(self) -> None:
    # self.cava_widget.styles.height = 3
    # self.cava_widget.styles.width = 86
    # self.cava_widget.styles.margin = (0, 0, 0, 0)
    # self.cava_widget.styles.padding = (0, 0)
    # self.cava_widget.styles.dock = "top"

    async def check_github(self) -> None:
        now = datetime.now(timezone.utc)
        if now - self.last_checked < timedelta(seconds=60):
            return
        self.last_checked = now
        commit_time = await asyncio.to_thread(
            get_recent_commit_time, self.username, self.repo, self.token
        )
        if commit_time and commit_time != self.last_valid_commit_time:
            self.last_valid_commit_time = commit_time
            self.tux.last_commit_time = commit_time
            self.tux.update_mood(commit_time)
            self.tux_widget.refresh()
            log(f"[✓] Fetched new commit time: {commit_time}")


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
