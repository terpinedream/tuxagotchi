from rich.panel import Panel
from rich.text import Text
from textual.widget import Widget
from textual.widgets import Static, Input
from textual.containers import Vertical
from rich import box


class TodoWidget(Widget):
    def __init__(self):
        super().__init__()
        self.todos = []
        self.input = Input(placeholder="TODO:")
        self.todo_display = Static()

    def compose(self):
        yield Vertical(
            self.todo_display,
            self.input,
        )

    async def on_mount(self):
        self.styles.height = "34"
        self.styles.width = "auto"
        self.input.styles.dock = "bottom"
        self.input.styles.background = "transparent"
        self.input.styles.border = ("round", "white")
        self.todo_display.styles.flex = 0
        self.todo_display.styles.overflow = "auto"  # enable scrolling if long

        await self.update_display()

    async def update_display(self):
        todo_text = "\n".join(f"> {todo}" for todo in self.todos) or ""
        panel = Panel(
            Text(todo_text),
            title="Todo List",
            box=box.ROUNDED,
        )
        self.todo_display.update(panel)

    async def on_input_submitted(self, event):
        self.todos.append(event.value.strip())
        self.input.value = ""
        await self.update_display()
