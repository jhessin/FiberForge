from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, OptionList, Static

from fiberforge.app.widgets.smart_input import SmartInput
from fiberforge.models.job import Job
from fiberforge.persistence.database import Database

# class JobMeta(Serializable):
#     job_type: JobType
#     region: JobRegion
#     task_name: str
#     company_name: str
#     address: str
#     lat: str = ''
#     long: str = ''
#     clli: str = ''
#     notes: str = 'No Notes'


class MetaScreen(Widget):
    BINDINGS = [
        ('enter', 'submit', 'Save Job'),
        ('escape', 'cancel', 'Cancel'),
    ]

    job: reactive[Optional[Job]] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static(f"Job ID = {self.job.id.value if self.job else 'None'}")
            yield OptionList(
                'Asbuilt',
                'Design',
            )
            yield SmartInput(
                label='Task Name:', id='task_name', placeholder='Enter the task name'
            )
            yield SmartInput(
                label='Company Name:',
                id='company_name',
                placeholder='Enter the company name',
            )
            yield SmartInput(
                label='Address', id='address', placeholder='Enter the address'
            )
            yield SmartInput(
                label='Lat/Long:',
                id='latlong',
                placeholder='Enter the latitude and longitude',
            )
            yield SmartInput(
                label='CLLI:', id='clli', placeholder='Enter the clli code.'
            )
            yield SmartInput(label='Notes:', id='notes', placeholder='Enter any notes')
            with Horizontal():
                yield Button('Save', id='save', variant='primary')
                yield Button('Cancel', id='cancel', variant='error')

    def update_job(self):
        if self.job:
            with Database() as db:
                self.job = db.jobs.by_id(self.job.id.value)

    @on(Input.Submitted)
    @on(Button.Pressed, '#save')
    def save(self, data: Input.Submitted | Button.Pressed):
        pass

    @on(Button.Pressed, '#cancel')
    def action_cancel(self):
        self.remove()
