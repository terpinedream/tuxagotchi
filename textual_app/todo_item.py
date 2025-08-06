from textual.widgets import Static


class TodoItem(Static):
    def __init__(self, text: str, index: int, selected: bool = False):
        super().__init__(text, classes="todo-item")
        self.index = index
        self.selected = selected
        self.update_style()

    def update_style(self):
        self.set_class(self.selected, "-selected")

    def render(self):
        return f"[reverse]{self.text}[/reverse]" if self.selected else self.text
