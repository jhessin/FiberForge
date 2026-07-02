from typing import Optional

import pyperclip
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Input, Label


class SmartInput(Widget):
    def __init__(self, label: Optional[str] = None, **input_kwargs) -> None:
        super().__init__()
        if label:
            self.label: Optional[Label] = Label(label)
        else:
            self.label = None
        self.input: Input = Input(**input_kwargs)

    def compose(self) -> ComposeResult:
        with Horizontal():
            if self.label:
                yield self.label
            yield self.input
            yield Button('Paste')

    @on(Button.Pressed)
    def paste(self):
        id_field = self.query_one(Input)
        id_field.value = pyperclip.paste()
