from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input

from fiberforge.models.ids import JobId
from fiberforge.models.job import Job


class JobScreen(ModalScreen[Optional[Job]]):

    BINDINGS = [
        ("enter", "submit", "Save Job"),
        ("escape", "dismiss(None)", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Input(
                name="id", restrict=r"[JB0-9]*", id="id", placeholder="Enter the Job ID"
            )
            yield Button("Save", id="save")
            # yield Button("Cancel", action="app.pop_screen()")
            yield Button("Cancel", id="cancel")

    # def on_button_pressed(self, btn: Button.Pressed):
    #     log("button was pressed !!!!!!")
    #     if btn.button.label == "Save":
    #         id = self.query_one(Input).value
    #         job = Job(JobId(id))
    #         self.dismiss(job)
    #     else:
    #         self.dismiss(None)
    #
    @on(Input.Submitted)
    @on(Button.Pressed, "#save")
    def save(self):
        id = self.query_one("#id", Input).value
        job = Job(JobId(id))
        self.dismiss(job)

    @on(Button.Pressed, "#cancel")
    def cancel(self):
        self.dismiss(None)
