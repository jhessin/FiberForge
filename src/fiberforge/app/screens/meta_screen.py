from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from fiberforge.app.widgets.smart_input import SmartInput
from fiberforge.models.job import Job, JobType
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
        ('enter', 'submit', 'Save Meta'),
        ('escape', 'cancel', 'Cancel'),
    ]

    job: reactive[Optional[Job]] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        """Compose the component here."""
        # TODO: Use the existing values to fill each input field in
        # meta/network/cfat screens
        folder = ''
        task_name = ''
        company_name = ''
        address = ''
        lat = ''
        long = ''
        clli = ''
        notes = ''

        if (job := self.job) and (meta := job.meta):
            folder = meta.region.folder
            task_name = meta.task_name
        with Vertical():
            yield Static(f"Job ID = {self.job.id.value if self.job else 'None'}")
            with Horizontal():
                yield Label('Job Type:')
                yield OptionList(
                    Option('Asbuilt', id='asbuilt'),
                    Option('Design', id='design'),
                    id='job_type',
                )
            if (
                self.job
                and self.job.meta
                and isinstance(self.job.meta.job_type, JobType.DESIGN)
            ):
                yield SmartInput(
                    label='Revision Number',
                    id='revision_number',
                    value=self.job.meta.job_type.revision_number,
                    type='number',
                )
            with Horizontal():
                yield Label('Region:')
                yield OptionList(
                    Option('MWR', id='region_mwr'),
                    Option('HOUSTON', id='region_houston'),
                    Option('BSR', id='region_bsr'),
                    id='region',
                )
            yield SmartInput(
                label='Folder:',
                id='folder',
                placeholder='Enter the folder name.',
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

    @on(OptionList.OptionSelected)
    def option_selected(self, data: OptionList.OptionSelected):
        """TODO: Parse all the options from the OptionList fields"""

    @on(Input.Submitted)
    @on(Button.Pressed, '#save')
    def save(self, data: Input.Submitted | Button.Pressed):
        """TODO: parse the information from the submitted field, or from all
        fields."""

    @on(Button.Pressed, '#cancel')
    def action_cancel(self):
        self.remove()
