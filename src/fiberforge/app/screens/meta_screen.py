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
    TextArea,
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


class MetaScreen(Widget):
    BINDINGS = [
        ('enter', 'submit', 'Save Meta'),
        ('escape', 'cancel', 'Cancel'),
    ]

    job: reactive[Optional[Job]] = reactive(None)

    def compose(self) -> ComposeResult:
        """Compose the component here."""

        with Vertical():
            """Begin yielding the fields here"""
            yield Static(f"Job ID = {self.job.id.value if self.job else 'None'}")

            with Horizontal():
                yield Label('Job Type:')
                yield Select(
                    (),
                    allow_blank=True,
                    id='job_type',
                )

            yield SmartInput(
                label='Revision Number',
                id='revision_number',
                type='number',
            )

            with Horizontal():
                yield Label('Region:')
                yield Select(
                    options=(),
                    allow_blank=True,
                    id='region',
                )
            yield SmartInput(
                label='Folder:',
                id='folder',
                placeholder='Enter the folder name.',
            )
            yield SmartInput(
                label='Task Name:',
                id='task_name',
                placeholder='Enter the task name',
            )
            yield SmartInput(
                label='Company Name:',
                id='company_name',
                placeholder='Enter the company name',
            )
            yield SmartInput(
                label='Address',
                id='address',
                placeholder='Enter the address',
            )
            yield SmartInput(
                label='Lat/Long:',
                id='latlong',
                placeholder='Enter the latitude and longitude',
            )
            yield SmartInput(
                label='CLLI:',
                id='clli',
                placeholder='Enter the clli code.',
            )
            yield Static('Notes:')
            yield TextArea(
                id='notes',
                placeholder='Enter any notes',
            )
            with Horizontal():
                yield Button('Save', id='save', variant='primary')
                yield Button('Cancel', id='cancel', variant='error')

    def watch_job(self, job: Job | None) -> None:
        """fill the components here."""
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

        if job and (meta := job.meta):
            job_type = meta.job_type
            region = meta.region
            folder = (
                meta.region.folder
                if meta.region and JobRegion.is_type(meta.region)
                else ''
            )
            task_name = meta.task_name
            company_name = meta.company_name
            address = meta.address
            lat = meta.lat
            long = meta.long
            clli = meta.clli
            notes = meta.notes

            job_type_select = self.query_one('#job_type', Select)
            job_type_select.set_options((
                ('ASBUILT', JobType.ASBUILT()),
                (
                    'DESIGN',
                    JobType.DESIGN()
                    if not isinstance(job_type, JobType.DESIGN)
                    else job_type,
                ),
            ))
            if JobType.is_type(job_type):
                job_type_select.value = job_type
            else:
                job_type_select.clear()

            revision_number_field = self.query_one('#revision_number', Input)
            if isinstance(meta.job_type, JobType.DESIGN):
                revision_number_field.value = str(meta.job_type.revision_number)
                revision_number_field.type = 'number'
                revision_number_field.disabled = False
            else:
                revision_number_field.value = 'Only Designs have a revision number'
                revision_number_field.disabled = True

            region_select = self.query_one('#region', Select)
            region_select.set_options((
                (
                    'MWR',
                    region if isinstance(region, JobRegion.MWR) else JobRegion.MWR(),
                ),
                (
                    'HOUSTON',
                    region
                    if isinstance(region, JobRegion.HOUSTON)
                    else JobRegion.HOUSTON(),
                ),
                (
                    'BSR',
                    region if isinstance(region, JobRegion.BSR) else JobRegion.BSR(),
                ),
            ))
            if JobRegion.is_type(region):
                region_select.value = region
            else:
                region_select.clear()

            folder_input = self.query_one('#folder', Input)
            folder_input.value = folder

            task_input = self.query_one('#task_name', Input)
            task_input.value = task_name

            company_input = self.query_one('#company_name', Input)
            company_input.value = company_name

            address_input = self.query_one('#address', Input)
            address_input.value = address

            if lat or long:
                latlong_input = self.query_one('#latlong', Input)
                latlong_input.value = f'{lat}, {long}'

            clli_input = self.query_one('#clli', Input)
            clli_input.value = clli

            notes_input = self.query_one('#notes', TextArea)
            notes_input.text = notes

    def update_meta(self, meta: JobMeta):
        assert self.job, 'job should be assigned by now.'
        with Database() as db:
            db.jobs.save(replace(self.job, meta=meta))
        self.post_message(UpdateDB())

    @on(Select.Changed)
    def option_selected(self, data: Select.Changed):
        """Parse all the options from the OptionList fields"""
        assert self.job, 'job should be assigned by now.'
        meta = self.job.meta or JobMeta()
        if data.control.id == 'region':
            meta = replace(
                meta,
                region=data.control.value
                if data.control.value is not Select.NULL
                else None,
            )
        else:
            meta = replace(
                meta,
                job_type=data.control.value
                if data.control.value is not Select.NULL
                else None,
            )
        self.update_meta(meta)

    @on(Input.Submitted)
    @on(Button.Pressed, '#save')
    def save(self, data: Input.Submitted | Button.Pressed):
        """Parse the information from the submitted field, or from all fields."""
        assert self.job, 'job should be assigned by now.'
        meta: JobMeta = self.job.meta or JobMeta()

        if isinstance(data, Button.Pressed):
            # TODO: queary and process all inputs
            pass
        else:
            match data.control.id:
                case 'revision_number':
                    if isinstance(meta.job_type, JobType.DESIGN):
                        meta = replace(
                            meta,
                            job_type=replace(meta.job_type, revision_number=data.value),
                        )
                case 'folder':
                    if meta.region:
                        meta = replace(
                            meta, region=replace(meta.region, folder=data.value)
                        )
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
