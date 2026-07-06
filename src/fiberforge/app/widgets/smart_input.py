from enum import Enum, auto
from typing import Optional

import pyperclip
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Input, Label


class SmartInput(Widget):
    class Type(Enum):
        Input = auto()
        Output = auto()
        Delete = auto()

    def __init__(
        self,
        *,
        types: list[Type] = [Type.Input],
        label: Optional[str] = None,
        **input_kwargs,
    ) -> None:
        super().__init__()
        if label:
            self.label: Optional[Label] = Label(label)
        else:
            self.label = None
        self.input: Input = Input(**input_kwargs)
        self.types: list[SmartInput.Type] = types

    def compose(self) -> ComposeResult:
        with Horizontal():
            if self.label:
                yield self.label
            yield self.input
            if SmartInput.Type.Input in self.types:
                yield Button('Paste')
            if SmartInput.Type.Output in self.types:
                yield Button('Copy')
            if SmartInput.Type.Delete in self.types:
                yield Button('Delete')

    @on(Button.Pressed)
    def pressed(self, data: Button.Pressed):
        data.stop()
        field = self.query_one(Input)
        if data.button.label == 'Paste':
            field.value = pyperclip.paste()
        elif data.button.label == 'Copy':
            pyperclip.copy(field.value)
        elif data.button.label == 'Delete':
            # TODO: delete the item
            pass
