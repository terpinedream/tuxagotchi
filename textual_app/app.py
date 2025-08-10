from datetime import datetime, timezone, timedelta
import asyncio
import os
import subprocess
from typing import Optional
from pacman import get_last_pacman_update_time
from textual.app import App
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Static, Input, Button
from textual.app import ComposeResult
from textual.events import Key
from textual import log
from textual_app.tux import Tux
from textual_app.tux_widget import TuxWidget
from config import load_config
from textual_app.ascii_loader import preload_ascii_frames
from rich.panel import Panel
from rich.text import Text
from rich import box


# UI Helper Functions (formerly in ui.py and ui_helpers.py)
def load_ascii(mood: str, tick: int) -> str:
    """Load ASCII art from two alternating files per mood for animation"""
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


def format_timedelta(td: timedelta) -> str:
    """Format timedelta into concise string (seconds, minutes, hours, days)"""
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
    """Generate block progress bar for mood countdowns"""
    if not hasattr(tux, "mood") or not hasattr(tux, "time_until_next_mood"):
        return "[Invalid Tux object]"

    countdown = tux.time_until_next_mood()
    if not countdown:
        return ""  # No countdown for sad/dead moods

    if tux.mood == "happy":
        total = 4 * 3600  # 4 hours in seconds
    elif tux.mood == "neutral":
        total = 24 * 3600  # 1 day in seconds
    else:
        return ""

    remaining = countdown.total_seconds()
    progress = 1 - (remaining / total)
    blocks_filled = int(progress * length)
    blocks_empty = length - blocks_filled

    animation = ["░", "▒", "▓", "█", "▓", "▒"]
    frame = animation[tick % len(animation)]

    if blocks_filled > 0:
        return "█" * (blocks_filled - 1) + frame + "░" * blocks_empty
    else:
        return frame + "░" * (length - 1)


def center_ascii(art: str, width: int = 32) -> str:
    """Center ASCII art horizontally given a target width"""
    lines = art.splitlines()
    return "\n".join(line.center(width) for line in lines)


def generate_css(colors: dict) -> str:
    """Generate CSS string with colors from config"""
    return f"""
Screen {{
  background: black;
  border: none;
  padding: 0;
  margin: 0;
}}

#main-container {{
    height: 100%;
    width: 100%;
    padding: 0 0 0 0;
}}

#tux-widget {{
    width: 60;
    padding: 1 2;
    margin: 1 0 0 0;
    border: round {colors["accent"]};
    background: {colors["background"]};
    color: {colors["foreground"]};
}}

#pacman-widget {{
    min-width: 20;
    max-width: 20;
    padding: 1 2;
    margin: 1 0 0 0;
    border: none;
    background: transparent;
    color: {colors["foreground"]};
    overflow-y: auto;
}}

#pacman-output {{
    border: round white;
    background: transparent;
    color: {colors["foreground"]};
}}

#pacman-button {{
    border: round white;
    background: transparent;
    color: {colors["foreground"]};
    margin: 1 0;
}}
"""


class PacmanWidget(Widget):
    """Widget that displays live terminal output from 'sudo pacman -Syu'"""

    can_focus = True

    def __init__(self, id: str = "pacman-widget"):
        super().__init__(id=id)
        self._is_running = False
        self.process = None
        self.waiting_for_password = False

    def compose(self) -> ComposeResult:
        self.output_display = Static(
            "Ready to update packages...\n\nClick 'Update System' to run 'sudo pacman -Syu'",
            id="pacman-output",
        )
        self.update_button = Button("Update System", id="pacman-button")
        self.password_input = Input(
            placeholder="Enter sudo password...", password=True, id="password-input"
        )
        self.password_input.display = False  # Hidden by default

        yield Vertical(
            self.output_display,
            self.password_input,
            self.update_button,
            id="pacman-container",
        )

    async def on_mount(self):
        # Set consistent sizing to match the old TODO widget
        self.output_display.styles.width = 35
        self.output_display.styles.min_width = 35
        self.output_display.styles.max_width = 35
        self.output_display.styles.height = (
            "24"  # Slightly smaller to make room for password input
        )
        self.output_display.styles.overflow = "auto"
        self.output_display.styles.scrollbar_size_vertical = 1
        self.output_display.styles.border = ("round", "white")
        self.output_display.styles.padding = (1, 2)

        # Style password input
        self.password_input.styles.width = 35
        self.password_input.styles.height = 3
        self.password_input.styles.border = ("round", "yellow")
        self.password_input.styles.margin = (1, 0)

        self.styles.width = 35
        self.styles.min_width = 35
        self.styles.max_width = 35

        container = self.query_one("#pacman-container")
        container.styles.width = 35
        container.styles.min_width = 35
        container.styles.max_width = 35

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle password submission"""
        if event.input.id == "password-input" and self.waiting_for_password:
            password = event.value
            self.password_input.value = ""
            self.password_input.display = False
            self.waiting_for_password = False

            # Send password to the process
            if self.process and password:
                try:
                    self.process.stdin.write(f"{password}\n".encode())
                    await self.process.stdin.drain()
                    self.output_display.update(
                        self.output_display.renderable + "\n[Password entered]"
                    )
                except Exception as e:
                    log(f"Error sending password: {e}")
                    self.output_display.update(
                        self.output_display.renderable
                        + f"\n❌ Error sending password: {e}"
                    )

    def show_password_input(self):
        """Show the password input field"""
        self.waiting_for_password = True
        self.password_input.display = True
        self.password_input.focus()
        self.output_display.update(
            self.output_display.renderable
            + "\n🔒 Sudo password required. Please enter password below:"
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "pacman-button" and not self._is_running:
            await self.run_pacman_update()

    async def run_pacman_update(self):
        """Run sudo pacman -Syu and display output in real-time"""
        if self._is_running:
            return

        self._is_running = True
        self.update_button.disabled = True
        self.update_button.label = "Updating..."
        self.output_display.update("Starting system update...\n")

        try:
            # Use subprocess.Popen for real-time output
            self.process = await asyncio.create_subprocess_exec(
                "sudo",
                "pacman",
                "-Syu",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                stdin=asyncio.subprocess.PIPE,
            )

            output_lines = []
            password_prompted = False

            # Read output line by line
            while True:
                try:
                    line = await asyncio.wait_for(
                        self.process.stdout.readline(), timeout=1.0
                    )
                    if not line:
                        break

                    decoded_line = line.decode("utf-8", errors="replace").rstrip()
                    output_lines.append(decoded_line)

                    # Check if sudo is asking for password
                    if not password_prompted and any(
                        keyword in decoded_line.lower()
                        for keyword in ["password", "[sudo]"]
                    ):
                        password_prompted = True
                        self.show_password_input()

                    # Update display with last 25 lines to prevent excessive scrolling
                    display_lines = output_lines[-25:]
                    self.output_display.update("\n".join(display_lines))

                    # Auto-scroll to bottom
                    self.output_display.scroll_end()

                except asyncio.TimeoutError:
                    # Check if process is still running
                    if self.process.poll() is not None:
                        break
                    continue

            # Wait for process to complete
            await self.process.wait()

            if self.process.returncode == 0:
                output_lines.append("\n✅ System update completed successfully!")
            else:
                output_lines.append(
                    f"\n❌ Update failed with exit code {self.process.returncode}"
                )

            # Final display update
            display_lines = output_lines[-25:]
            self.output_display.update("\n".join(display_lines))
            self.output_display.scroll_end()

        except Exception as e:
            error_msg = f"❌ Error running pacman update: {str(e)}"
            self.output_display.update(error_msg)
            log(f"Pacman update error: {e}")

        finally:
            self._is_running = False
            self.waiting_for_password = False
            self.password_input.display = False
            self.update_button.disabled = False
            self.update_button.label = "Update System"
            self.process = None

    async def on_key(self, event: Key) -> None:
        # Allow ESC to cancel running update
        if event.key == "escape" and self._is_running and self.process:
            try:
                self.process.terminate()
                self.output_display.update(
                    self.output_display.renderable + "\n\n🚫 Update cancelled by user"
                )
            except Exception as e:
                log(f"Error cancelling pacman update: {e}")
            event.stop()


class TuxApp(App):
    """Main Tuxagotchi Textual App"""

    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = "styles.css"

    async def on_mount(self) -> None:
        # Preload ascii for better performance
        preload_ascii_frames()

        # Load config for theme colors
        config = load_config()
        self.theme_colors = config["colors"]

        # Pacman update tracking
        self.last_valid_update_time = None
        self.last_checked = datetime.min.replace(tzinfo=timezone.utc)

        # Initialize Tux logic and UI
        self.tux = Tux(username="arch", repo="system-updates")
        self.tux_widget = TuxWidget(self.tux, "pacman-updates")
        self._style_tux_widget()

        # Replace TODO widget with Pacman widget
        self.pacman_widget = PacmanWidget(id="pacman-widget")
        self._style_pacman_widget()

        top_row = Horizontal(self.tux_widget, self.pacman_widget, id="main-container")
        await self.mount(top_row)

        # Updated keybinds bar (removed TODO-specific bindings, added pacman info)
        self.keybinds = Static(
            "[bold][/bold]【q ➡ Quit】【Click Button ➡ Update】【ESC ➡ Cancel Update】",
            id="keybinds",
        )
        self.keybinds.styles.dock = "bottom"
        self.keybinds.styles.height = 1
        self.keybinds.styles.background = "transparent"
        self.keybinds.styles.color = "white"
        self.keybinds.styles.padding = (0, 1)
        await self.mount(self.keybinds)

        # Check for pacman updates every 30 seconds
        self.set_interval(3, self.check_pacman_updates)

    def _style_tux_widget(self) -> None:
        self.tux_widget.styles.padding = (0, 0)
        self.tux_widget.styles.height = 35
        self.tux_widget.styles.width = 50
        self.tux_widget.styles.margin = (0, 0, 0, 0)

    def _style_pacman_widget(self) -> None:
        """Style the pacman widget to match the old TODO widget dimensions"""
        self.pacman_widget.styles.width = 20
        self.pacman_widget.styles.min_width = 20
        self.pacman_widget.styles.max_width = 20
        self.pacman_widget.styles.height = 35
        self.pacman_widget.styles.max_height = 35
        self.pacman_widget.styles.margin = (0, 0, 0, 0)
        self.pacman_widget.styles.padding = (0, 0)

    async def check_pacman_updates(self) -> None:
        now = datetime.now(timezone.utc)
        if now - self.last_checked < timedelta(seconds=3):
            return
        self.last_checked = now

        update_time = await asyncio.to_thread(get_last_pacman_update_time)
        if update_time and update_time != self.last_valid_update_time:
            self.last_valid_update_time = update_time
            self.tux.last_update_time = update_time
            self.tux.update_mood(update_time)
            self.tux_widget.refresh()
            log(f"[✓] Last pacman update: {update_time}")


def generate_css_file():
    """Generate the CSS file with current config colors"""
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
