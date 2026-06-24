from typing import Optional

from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.reactive import reactive
from textual.widgets import Button, Label, Static

from fiberforge.models.job import Job


class JobDetails(Static):
    job: reactive[Optional[Job]] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        with VerticalGroup():
            yield Label(self.job.label if self.job else 'No Job Selected', id='JobName')
            if self.job is not None:
                with HorizontalGroup():
                    with VerticalGroup(id='metagroup'):
                        yield Button('View Meta', disabled=self.job.meta is None)
                        yield Button('Edit Meta' if self.job.meta else 'Create Meta')
                    with VerticalGroup(id='networkgroup'):
                        yield Button(
                            'View Network Info', disabled=self.job.network is None
                        )
                        yield Button(
                            'Edit Network info'
                            if self.job.network
                            else 'Create Network Info'
                        )
                    with VerticalGroup(id='cfatgroup'):
                        yield Button('View CFAT info', disabled=self.job.cfat is None)
                        yield Button('Edit CFAT' if self.job.cfat else 'Create CFAT')
