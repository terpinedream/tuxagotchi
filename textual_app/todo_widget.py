from textual.widget import Widget
from textual.widgets import Static, Input
from textual.containers import Vertical
from textual.app import ComposeResult
from rich.panel import Panel
from rich.text import Text
from rich import box


class TodoWidget(Widget):
    def __init__(self, id: str = "todo-widget"):
        super().__init__(id=id)
        self.todos = []

    def compose(self) -> ComposeResult:
        self.todo_display = Static(id="todo-display")
        self.input = Input(placeholder="TODO:", id="todo-input")

        yield Vertical(
            self.todo_display,
            self.input,
            id="todo-container",
        )

    async def on_mount(self):
        # Fix size on internal widgets too:
        self.todo_display.styles.width = 35
        self.todo_display.styles.min_width = 35
        self.todo_display.styles.max_width = 35

        self.styles.width = 35
        self.styles.min_width = 35
        self.styles.max_width = 35

        container = self.query_one("#todo-container")
        container.styles.width = 35
        container.styles.min_width = 35
        container.styles.max_width = 35

        self.todo_display.styles.height = "32"
        self.todo_display.styles.overflow = "auto"
        self.todo_display.styles.scrollbar_size_vertical = 1
        self.input.styles.dock = "bottom"

        await self.update_display()

    async def update_display(self):
        lines = [f"↳  {todo}" for todo in self.todos]
        todo_text = Text("\n".join(lines), overflow="fold")  # wrap long lines

        panel = Panel(
            todo_text,
            title="TODO",
            box=box.ROUNDED,
            width=50,  # fixed width
        )
        self.todo_display.styles.width = 50  # also fix the widget container width
        self.todo_display.update(panel)

    async def on_input_submitted(self, event: Input.Submitted):
        value = event.value.strip()
        if value:
            self.todos.append(value)
            self.input.value = ""
            await self.update_display()
