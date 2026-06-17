# fiberforge/ui/forms/base_form.py

from __future__ import annotations

from typing import Any, List, Optional

import pyperclip
from textual import events
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Static, Input
from textual.containers import Vertical
from textual.binding import Binding
from textual.reactive import reactive


def collapse_whitespace(text: str) -> str:
    """Collapse all whitespace (including newlines) into single spaces."""
    return " ".join(text.split())


class FormField(Static):
    """Label + single-line Input, with required/optional support."""

    def __init__(
        self,
        label: str,
        value: str = "",
        *,
        name: str,
        required: bool = False,
        input_widget: Optional[Widget] = None,
    ):
        super().__init__()
        self.field_name = name
        self.label_text = label
        self.required = required
        self.input: Widget = input_widget or Input(value=value)
        self.input.can_focus = True

    def compose(self):
        # Required fields get a color or prefix
        req_prefix = "[red]*[/red] " if self.required else ""
        yield Static(req_prefix + self.label_text, classes="form-label")
        yield self.input

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


class FormScreen(ModalScreen):
    """
    Generic vim-style form:

    - j/k: move between fields
    - Enter: enter insert mode on current field
    - Esc: return to normal mode
    - Y: yank current field value to system clipboard
    - P: paste from system clipboard (whitespace-collapsed)
    """

    BINDINGS = [
        Binding("j", "down", "Down"),
        Binding("k", "up", "Up"),
        Binding("enter", "edit", "Edit"),
        Binding("i", "edit", "Edit"),
        Binding("escape", "normal_mode", "Normal"),
        Binding("y", "yank", "Yank"),
        Binding("p", "paste", "Paste"),
    ]

    mode: reactive[str] = reactive("normal")  # "normal" | "insert"
    current_index: reactive[int] = reactive(0)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._fields: List[FormField] = []

    # ---- override this in concrete forms ----

    def build_fields(self) -> list[FormField]:
        """
        Return a list of FormField instances.

        Example in a subclass:
            return [
                FormField("Job ID", job.id.value, name="id"),
                FormField("Description", job.description, name="description"),
            ]
        """
        raise NotImplementedError

    def collect_data(self) -> dict[str, str]:
        """Collect current field values into a simple dict."""
        return {f.field_name: f.value for f in self._fields}

    # ---- Textual lifecycle ----

    def compose(self):
        container = Vertical(id="form")
        yield container
        yield Static("", id="status")

    def on_mount(self):
        self._fields = self.build_fields()
        container = self.query_one(Vertical)
        for field in self._fields:
            container.mount(field)

    @property
    def status(self) -> Static:
        return self.query_one("#status", Static)

    # ---- navigation helpers ----

    def _clamp_index(self) -> None:
        if not self._fields:
            self.current_index = 0
            return
        self.current_index = max(0, min(self.current_index, len(self._fields) - 1))

    def _current_field(self) -> FormField | None:
        if not self._fields:
            return None
        self._clamp_index()
        return self._fields[self.current_index]

    # ---- actions ----

    def action_down(self) -> None:
        if not self._fields or self.mode == "insert":
            return
        self.current_index += 1
        self._clamp_index()

    def action_up(self) -> None:
        if not self._fields or self.mode == "insert":
            return
        self.current_index -= 1
        self._clamp_index()

    def action_edit(self) -> None:
        field = self._current_field()
        if field is None:
            return
        self.mode = "insert"
        field.focus_input()
        self.status.update(f"INSERT — {field.field_name}")

    def action_normal_mode(self) -> None:
        field = self._current_field()
        if field is not None:
            field.blur_input()
        self.mode = "normal"
        self.status.update("NORMAL")

    def action_yank(self) -> None:
        field = self._current_field()
        if field is None:
            return
        pyperclip.copy(field.value)
        self.status.update(f"Yanked {field.field_name} to clipboard")

    def action_paste(self) -> None:
        field = self._current_field()
        if field is None:
            return

        text = collapse_whitespace(pyperclip.paste() or "")

        if self.mode == "normal":
            field.value = text
        elif isinstance(field.input, Input):
            field.input.insert_text_at_cursor(text)

        self.status.update(f"Pasted into {field.field_name}")

    def set_required(self, field_name: str, required: bool) -> None:
        for f in self._fields:
            if f.field_name == field_name:
                f.set_required(required)
                break

    async def on_key(self, event: events.Key) -> None:
        # INSERT MODE: only Esc is special
        if self.mode == "insert":
            if event.key == "escape":
                self.action_normal_mode()
                event.stop()
            else:
                # Let Input handle the key normally
                return

        # NORMAL MODE: use bindings
        return await super()._on_key(event)
