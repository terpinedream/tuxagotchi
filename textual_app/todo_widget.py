from textual.widget import Widget
from textual.widgets import Static, Input
from textual.containers import Vertical
from textual.app import ComposeResult
from textual.events import Key

from rich.panel import Panel
from rich.text import Text
from rich import box

from .todo_item import TodoItem


class TodoWidget(Widget):
    can_focus = True  # <-- so widget receives key events

    def __init__(self, id: str = "todo-widget"):
        super().__init__(id=id)
        self.todos: list[str] = []
        self.selected_index: int = 0
        self.insert_mode: bool = False

    def compose(self) -> ComposeResult:
        self.todo_display = Static(id="todo-display")
        self.input = Input(placeholder="TODO:", id="todo-input")

        yield Vertical(
            self.todo_display,
            self.input,
            id="todo-container",
        )

    async def on_mount(self):
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

        # Not in insert mode: blur input and focus this widget so keys work immediately
        self.insert_mode = True
        self.input.focus()

        await self.update_display()

    async def update_display(self):
        lines = []

        for i, todo in enumerate(self.todos):
            bullet = "◦"
            if i == self.selected_index:
                line = Text(f"► {bullet} {todo}", style="bold")
            else:
                line = Text(f"  {bullet} {todo}")
            lines.append(line)

        todo_text = Text()
        for line in lines:
            todo_text.append(line)
            todo_text.append("\n")

        panel = Panel(
            todo_text,
            title="TODO",
            box=box.ROUNDED,
            width=50,
        )
        self.todo_display.update(panel)

    async def on_input_submitted(self, event: Input.Submitted):
        value = event.value.strip()
        if value:
            self.todos.append(value)
            self.input.value = ""
            self.selected_index = len(self.todos) - 1
            await self.update_display()

        # Stay in insert mode after submitting; keep input focused for easy entry
        self.insert_mode = True
        self.input.focus()

    async def on_key(self, event: Key) -> None:
        if self.insert_mode:
            if event.key == "escape":
                self.insert_mode = False
                self.input.blur()
                self.focus()
                event.stop()
            return

        if not self.todos:
            return

        if event.key == "j":
            self.selected_index = (self.selected_index + 1) % len(self.todos)
            await self.update_display()
            event.stop()
        elif event.key == "k":
            self.selected_index = (self.selected_index - 1) % len(self.todos)
            await self.update_display()
            event.stop()
        elif event.key == "x":
            self.todos.pop(self.selected_index)
            self.selected_index = max(0, self.selected_index - 1)
            await self.update_display()
            event.stop()
        elif event.key == "a":
            self.insert_mode = True
            self.input.focus()
            event.stop()
        elif event.key == "escape":
            event.stop()
