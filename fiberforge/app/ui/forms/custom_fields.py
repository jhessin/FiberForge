from typing import Optional

import pyperclip

from textual.widgets import Static, Input, Button
from textual.containers import Vertical, Horizontal


def collapse_whitespace(text: str) -> str:
    """Collapse all whitespace (including newlines) into single spaces."""
    return " ".join(text.split())


class InputField(Static):
    """Label + single-line Input, with required/optional support."""

    def __init__(
        self,
        label: str,
        value: str = "",
        *args,
        name: str,
        required: bool = False,
        input_widget: Optional[Input] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.field_name = name
        self.label_text = label
        self.required = required
        self.input: Input = input_widget or Input(value=value)
        self.input.can_focus = True

    def compose(self):
        # Required fields get a color or prefix
        req_prefix = "[red]*[/red] " if self.required else ""
        with Vertical():
            yield Static(req_prefix + self.label_text, classes="form-label")
            with Horizontal():
                yield self.input
                yield Button("Copy")
                yield Button("Paste")

    @property
    def value(self) -> str:
        if isinstance(self.input, Input):
            return self.input.value
        return ""

    @value.setter
    def value(self, v: str) -> None:
        if isinstance(self.input, Input):
            self.input.value = v

    def focus_input(self) -> None:
        self.input.focus()

    def blur_input(self) -> None:
        self.input.blur()

    def set_required(self, required: bool) -> None:
        """Toggle required state at runtime and refresh label."""
        self.required = required
        self.refresh()  # Re-render the label

    def on_button_pressed(self, event: Button.Pressed):
        match event.button.label:
            case "Copy":
                pyperclip.copy(self.value)
            case "Paste":
                self.value = collapse_whitespace(pyperclip.paste() or "")
