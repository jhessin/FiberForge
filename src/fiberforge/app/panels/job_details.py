from typing import Optional

from textual.app import ComposeResult
from textual.containers import Grid
from textual.reactive import reactive
from textual.widgets import Label, Static

from fiberforge.models.job import Job


class JobDetails(Static):
    job: reactive[Optional[Job]] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        with Grid():
            yield Label(self.job.label if self.job else 'No Job Selected')
