from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Button, Label, Static

from fiberforge.app.messages import UpdateDetail
from fiberforge.app.screens.meta_screen import MetaScreen
from fiberforge.app.widgets.utils import FocusButton
from fiberforge.models.job import Job


class JobDetails(Static):
    job: reactive[Optional[Job]] = reactive(None, recompose=True)

    class Ready(Message):
        pass

    def compose(self) -> ComposeResult:
        with VerticalGroup():
            yield Label(self.job.label if self.job else 'No Job Selected', id='JobName')
            if self.job is not None:
                with HorizontalGroup():
                    with VerticalGroup(id='metagroup'):
                        yield Button('View Meta', disabled=self.job.meta is None)
                        yield FocusButton(
                            'Edit Meta' if self.job.meta else 'Create Meta',
                            id='editmetabutton',
                        )
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

    @on(Button.Pressed, '#editmetabutton')
    def edit_meta(self):
        self.post_message(UpdateDetail(MetaScreen().data_bind(JobDetails.job)))
