from enum import Enum, auto
from typing import Optional

import pyperclip
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Button, Input, Label, Static


class SmartInput(Widget):
    class Type(Enum):
        Input = auto()
        Output = auto()
        Delete = auto()

    def __init__(
        self,
        *,
        # types: Iterable[Type] = [Type.Input],
        label: Optional[str] = None,
        **input_kwargs,
    ) -> None:
        super().__init__()
        if label:
            self.label: Optional[Label] = Label(label)
        else:
            self.label = None
        self.input: Input = Input(**input_kwargs)
        # self.types: set[SmartInput.Type] = set(types)

    def compose(self) -> ComposeResult:
        with Horizontal():
            if self.label:
                yield self.label
            yield self.input
            yield Button('Paste')
            yield Button('Clear')

    @on(Button.Pressed)
    def pressed(self, data: Button.Pressed):
        data.stop()
        field = self.query_one(Input)
        if data.button.label == 'Paste':
            field.value = pyperclip.paste()
        elif data.button.label == 'Clear':
            field.value = ''


class SmartOutput(Widget):
    def __init__(self, renderable: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.renderable: str = renderable

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield Static(self.renderable)
            yield Button('Copy')

    @on(Button.Pressed)
    def pressed(self, data: Button.Pressed):
        data.stop()
        if data.button.label == 'Copy':
            pyperclip.copy(self.renderable)
