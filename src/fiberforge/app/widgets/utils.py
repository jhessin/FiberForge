from textual.widgets import Button, Input

from .smart_input import SmartInput


class FocusButton(Button):
    def on_mount(self):
        self.focus()


class FocusInput(SmartInput):
    def on_mount(self):
        self.query_one(Input).focus()
