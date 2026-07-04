from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Input, Static

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


class CfatScreen(Widget):
    BINDINGS = [
        ('enter', 'submit', 'Save Network'),
        ('escape', 'cancel', 'Cancel'),
    ]

    job: reactive[Optional[Job]] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        """Compose the component here."""
        # Front load all the listed items
        mux_item: Static = Static()
        distance_item: Static = Static()
        bandwidth_item: Static = Static()
        preterm_item: Static = Static()
        ext_id_item: Static = Static()

        if (job := self.job) and (cfat := job.cfat):
            mux_item = (
                Static(cfat.mux_id.value) if cfat.mux_id.value else Static('No Mux')
            )
            distance_item = (
                Static(str(cfat.distance_to_hub))
                if cfat.distance_to_hub
                else Static('No Distance Specified')
            )
            bandwidth_item = Static(str(cfat.bandwidth))
            preterm_item = (
                Static(cfat.preterm) if cfat.preterm else Static('No Preterm Specified')
            )
            ext_id_item = (
                Static(cfat.ext_id) if cfat.ext_id else Static('No EXT_ID Specified')
            )

        with Vertical():
            yield Static(f"Job ID = {self.job.id.value if self.job else 'None'}")

            yield Static('MUX:')
            yield mux_item
            yield SmartInput(
                label='Mux:',
                id='mux',
                placeholder='Mux by id',
            )

            yield Static('DISTANCE TO HUB:')
            yield distance_item
            yield SmartInput(
                label='Distance:',
                id='distance_to_hub',
                placeholder='Enter the discance from hub to endsite',
            )
            yield Static('BANDWIDTH:')
            yield bandwidth_item
            yield SmartInput(
                label='Bandwidth:',
                id='bandwidth',
                placeholder='Enter the bandwidth required',
                type='number',
            )
            yield Static('PRETERM:')
            yield preterm_item
            yield SmartInput(
                label='Preterm:',
                id='preterm',
                placeholder='Enter the preterm',
            )
            yield Static('EXT_ID:')
            yield ext_id_item
            yield SmartInput(
                label='EXT_ID:',
                id='ext_id',
                placeholder='Enter the ext_id from EP',
            )
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
        """TODO: parse the information from the submitted field, or from all
        fields if the type of data is Button.Pressed."""

    @on(Button.Pressed, '#cancel')
    def action_cancel(self):
        self.remove()
