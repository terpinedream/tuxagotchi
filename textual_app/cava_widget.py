import asyncio
from textual.widget import Widget
from textual.widgets import Static
from textual.containers import Vertical
from textual.app import ComposeResult, App
from rich.panel import Panel
from rich.text import Text
from rich import box
import tempfile
import os


CAVA_CONFIG = """
[general]
bars = 80

[output]
method = "raw"
raw_target = "/dev/stdout"
data_format = "ascii"
ascii_max_range = 8

[raw]
bit_format = "8bit"
"""


class CavaWidget(Widget):
    def __init__(self, id: str = "cava-widget"):
        super().__init__(id=id)
        self.cava_display = Static(id="cava-display")
        self._cava_task = None

    def compose(self) -> ComposeResult:
        yield Vertical(
            self.cava_display,
            id="cava-container",
        )

    async def on_mount(self):
        # Write a temporary cava config file
        self.cava_config_path = tempfile.NamedTemporaryFile(delete=False).name
        with open(self.cava_config_path, "w") as f:
            f.write(CAVA_CONFIG)

        # Launch cava and stream output
        self._cava_task = asyncio.create_task(self.run_cava())

    async def run_cava(self):
        process = await asyncio.create_subprocess_exec(
            "cava",
            "-p",
            self.cava_config_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )

        while True:
            if process.stdout.at_eof():
                break

            line = await process.stdout.readline()
            if not line:
                continue

            # Parse raw ASCII output (one line = list of numbers separated by semicolons)
            raw = line.decode("utf-8").strip()
            if not raw:
                continue

            bars = [int(x) for x in raw.split(";") if x.isdigit()]
            visual = self.render_bars(bars)

            panel = Panel(
                Text(visual, justify="center"),
                title="Audio Visualizer",
                border_style="white",
                box=box.ROUNDED,
            )
            self.cava_display.update(panel)

    def render_bars(self, bars):
        # Convert each bar value to blocks
        return "".join("▁▂▃▄▅▆▇█"[min(val, 7)] for val in bars)

    async def on_unmount(self):
        # Clean up config file
        if hasattr(self, "cava_config_path"):
            os.remove(self.cava_config_path)


class TestApp(App):
    async def on_mount(self):
        cava = CavaWidget()
        await self.mount(cava)


if __name__ == "__main__":
    TestApp().run()
