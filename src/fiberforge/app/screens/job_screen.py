from dataclasses import dataclass

import pyperclip
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input

from fiberforge.app.widgets.utils import FocusInput
from fiberforge.models.ids import JobId
from fiberforge.models.job import Job


class JobScreen(Widget):
    BINDINGS = [
        ('enter', 'submit', 'Save Job'),
        ('escape', 'cancel', 'Cancel'),
    ]

    @dataclass
    class NewJob(Message):
        job: Job

    def compose(self) -> ComposeResult:
        with Vertical():
            yield FocusInput(id='id', placeholder='Enter the Job ID from EP')
            with Horizontal():
                yield Button('Save', id='save', variant='primary')
                yield Button('Cancel', id='cancel', variant='error')

    @on(Input.Submitted)
    @on(Button.Pressed, '#save')
    def save(self):
        id = self.query_one('#id', Input).value
        job = Job(JobId(id))
        self.post_message(JobScreen.NewJob(job))
        self.remove()

    @on(Button.Pressed, '#cancel')
    def action_cancel(self):
        self.remove()

    @on(Button.Pressed, '#paste')
    def action_paste(self):
        id_field = self.query_one('#id', Input)
        id_field.value = pyperclip.paste()
