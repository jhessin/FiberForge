from dataclasses import replace
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import (
    Button,
    Input,
    Label,
    Select,
    Static,
)

from fiberforge.app.messages import UpdateDB
from fiberforge.app.widgets.smart_input import SmartInput
from fiberforge.models.job import (
    Job,
    JobMeta,
    JobRegion,
    JobType,
)
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
        job_type: JobType.Type | None = None
        region: JobRegion.Type | None = None
        folder = ''
        task_name = ''
        company_name = ''
        address = ''
        lat = ''
        long = ''
        clli = ''
        notes = ''

        if (job := self.job) and (meta := job.meta):
            job_type = meta.job_type
            region = meta.region
            folder = meta.region.folder if meta.region else ''
            task_name = meta.task_name
            company_name = meta.company_name
            address = meta.address
            lat = meta.lat
            long = meta.long
            clli = meta.clli
            notes = meta.notes

        with Vertical():
            """Begin yielding the fields here"""
            yield Static(f"Job ID = {self.job.id.value if self.job else 'None'}")

            with Horizontal():
                yield Label('Job Type:')
                yield Select[JobType.Type](
                    (
                        ('ASBUILT', JobType.ASBUILT()),
                        (
                            'DESIGN',
                            JobType.DESIGN()
                            if not isinstance(job_type, JobType.DESIGN)
                            else job_type,
                        ),
                    ),
                    value=job_type or Select.NULL,
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
                    value=str(self.job.meta.job_type.revision_number),
                    type='number',
                )
            with Horizontal():
                yield Label('Region:')
                yield Select[JobRegion.Type](
                    options=(
                        (
                            'MWR',
                            region
                            if isinstance(region, JobRegion.MWR)
                            else JobRegion.MWR(),
                        ),
                        (
                            'HOUSTON',
                            region
                            if isinstance(region, JobRegion.HOUSTON)
                            else JobRegion.HOUSTON(),
                        ),
                        (
                            'BSR',
                            region
                            if isinstance(region, JobRegion.BSR)
                            else JobRegion.BSR(),
                        ),
                    ),
                    value=region or Select.NULL,
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

    def update_meta(self, meta: JobMeta):
        assert self.job, 'job should be assigned by now.'
        with Database() as db:
            db.jobs.save(replace(self.job, meta=meta))
        self.post_message(UpdateDB())

    @on(Select.Changed)
    def option_selected(self, data: Select.Changed):
        """Parse all the options from the OptionList fields"""
        self.log.debug('Select.Changed has been successfully called')
        assert self.job, 'job should be assigned by now.'
        meta = self.job.meta or JobMeta()
        if data.control.id == 'region':
            meta = replace(meta, region=data.control.value)
        else:
            meta = replace(meta, job_type=data.control.value)
        self.update_meta(meta)

    @on(Input.Submitted)
    @on(Button.Pressed, '#save')
    def save(self, data: Input.Submitted):
        """Parse the information from the submitted field, or from all fields."""
        assert self.job, 'job should be assigned by now.'
        meta: JobMeta = self.job.meta or JobMeta()
        self.log.debug('save has been successfully called')
        match data.control.id:
            case 'revision_number':
                if isinstance(meta.job_type, JobType.DESIGN):
                    meta = replace(
                        meta,
                        job_type=replace(meta.job_type, revision_number=data.value),
                    )
            case 'folder':
                if meta.region:
                    meta = replace(meta, region=replace(meta.region, folder=data.value))
            case 'task_name':
                meta = replace(meta, task_name=data.value)
            case 'company_name':
                meta = replace(meta, company_name=data.value)
            case 'address':
                meta = replace(meta, address=data.value)
            case 'latlong':
                (lat, long) = data.value.split(',')
                meta = replace(
                    meta,
                    lat=lat.strip(),
                    long=long.strip(),
                )
            case 'clli':
                meta = replace(meta, clli=data.value)
            case 'notes':
                meta = replace(meta, notes=data.value)
        self.update_meta(meta)

    @on(Button.Pressed, '#cancel')
    def action_cancel(self):
        self.remove()
