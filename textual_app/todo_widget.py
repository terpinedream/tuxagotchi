from textual.widget import Widget
from textual.widgets import Static, Input
from textual.containers import Vertical
from textual.app import ComposeResult


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
        await self.update_display()

    async def update_display(self):
        todo_text = "\n".join(f"• {todo}" for todo in self.todos) or ""
        self.todo_display.update(todo_text)

    async def on_input_submitted(self, event: Input.Submitted):
        value = event.value.strip()
        if value:
            self.todos.append(value)
            self.input.value = ""
            await self.update_display()
