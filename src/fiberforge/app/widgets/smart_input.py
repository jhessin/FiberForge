from textual import on
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Input, Button
from textual.app import ComposeResult

import pyperclip


class SmartInput(Widget):
    DEFAULT_CSS = """
    Input {
        width: 3fr;
    }

    Button {
        width: 1fr;
    }
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.input: Input = Input(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.input
            yield Button("Paste", id="paste")

    @on(Button.Pressed, "#paste")
    def paste(self):
        id_field = self.query_one(Input)
        id_field.value = pyperclip.paste()
