from dataclasses import replace
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Label, OptionList, Static
from textual.widgets.option_list import Option

from fiberforge.app.messages import UpdateDB
from fiberforge.app.widgets.smart_input import SmartInput
from fiberforge.models.job import Job, JobMeta, JobRegion, JobType
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
        job_type = ''
        region = ''
        folder = ''
        task_name = ''
        company_name = ''
        address = ''
        lat = ''
        long = ''
        clli = ''
        notes = ''

        if (job := self.job) and (meta := job.meta):
            job_type = (
                'asbuilt' if isinstance(meta.job_type, JobType.ASBUILT) else 'design'
            )
            region = (
                'region_mwr'
                if isinstance(meta.region, JobRegion.MWR)
                else 'region_houston'
                if isinstance(meta.region, JobRegion.HOUSTON)
                else 'region_bsr'
            )
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
                type_options = OptionList(
                    Option('Asbuilt', id='asbuilt'),
                    Option('Design', id='design'),
                    id='job_type',
                )
                type_options.highlighted = 1 if job_type == 'design' else 0
                yield type_options
            if (
                self.job
                and self.job.meta
                and isinstance(self.job.meta.job_type, JobType.DESIGN)
            ):
                yield SmartInput(
                    label='Revision Number',
                    id='revision_number',
                    value=str(self.job.meta.job_type.revision_number),
                    type='number',
                )
            with Horizontal():
                yield Label('Region:')
                region_options = OptionList(
                    Option('MWR', id='region_mwr'),
                    Option('HOUSTON', id='region_houston'),
                    Option('BSR', id='region_bsr'),
                    id='region',
                )
                region_options.highlighted = (
                    1
                    if region == 'region_houston'
                    else 0
                    if region == 'region_mwr'
                    else 2
                )
                yield region_options
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
        """Parse all the options from the OptionList fields"""
        assert self.job, 'job should be assigned by now.'
        meta = self.job.meta or JobMeta()
        if data.control.id == 'region':
            new_meta = replace(
                meta,
                region=JobRegion.BSR()
                if data.option_id == 'region_bsr'
                else JobRegion.HOUSTON()
                if data.option_id == 'region_houston'
                else JobRegion.MWR(),
            )
        else:
            new_meta = replace(
                meta,
                job_type=JobType.ASBUILT()
                if data.option_id == 'asbuilt'
                else JobType.DESIGN(),
            )
        with Database() as db:
            db.jobs.save(replace(self.job, meta=new_meta))

    @on(Input.Submitted)
    @on(Button.Pressed, '#save')
    def save(self, data: Input.Submitted | Button.Pressed):
        """Parse the information from the submitted field, or from all fields."""
        # TODO:
        self.post_message(UpdateDB())

    @on(Button.Pressed, '#cancel')
    def action_cancel(self):
        self.remove()
