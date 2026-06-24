from typing import Optional

from textual.app import ComposeResult
from textual.containers import Container
from textual.reactive import reactive
from textual.widgets import Label, Placeholder, Static

from fiberforge.models.job import Job


class JobDetails(Static):
    job: reactive[Optional[Job]] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(self.job.label if self.job else 'No Job Selected', id='JobName')
            yield Placeholder(classes='button')
            yield Placeholder(classes='button')
            yield Placeholder(classes='button')
            yield Placeholder(classes='button')
            yield Placeholder(classes='button')
            yield Placeholder(classes='button')
