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
        folder = ''
        task_name = ''
        company_name = ''
        address = ''
        lat = ''
        long = ''
        clli = ''
        notes = ''

        if (job := self.job) and (meta := job.meta):
            folder = meta.region.folder if meta.region else ''
            task_name = meta.task_name
            company_name = meta.company_name
            address = meta.address
            lat = meta.lat
            long = meta.long
            clli = meta.clli
            notes = meta.notes

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
                value=folder,
                placeholder='Enter the folder name.',
                types=(
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ),
            )
            yield SmartInput(
                label='Task Name:',
                id='task_name',
                value=task_name,
                placeholder='Enter the task name',
                types=(
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ),
            )
            yield SmartInput(
                label='Company Name:',
                id='company_name',
                value=company_name,
                placeholder='Enter the company name',
                types=(
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ),
            )
            yield SmartInput(
                label='Address',
                id='address',
                value=address,
                placeholder='Enter the address',
                types=(
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ),
            )
            yield SmartInput(
                label='Lat/Long:',
                id='latlong',
                value=f'{lat}, {long}' if lat or long else '',
                placeholder='Enter the latitude and longitude',
                types=(
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ),
            )
            yield SmartInput(
                label='CLLI:',
                id='clli',
                value=clli,
                placeholder='Enter the clli code.',
                types=(
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ),
            )
            yield SmartInput(
                label='Notes:',
                id='notes',
                value=notes,
                placeholder='Enter any notes',
                types=(
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ),
            )
            with Horizontal():
                yield Button('Save', id='save', variant='primary')
                yield Button('Cancel', id='cancel', variant='error')

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
