import pyperclip
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Input


class SmartInput(Widget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__()
        self.input: Input = Input(*args, **kwargs)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield self.input
            yield Button('Paste', id='paste')

    @on(Button.Pressed, '#paste')
    def paste(self):
        id_field = self.query_one(Input)
        id_field.value = pyperclip.paste()
