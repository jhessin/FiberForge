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
        mux: str = ''
        distance: int = 0
        bandwidth: int = 0
        preterm: str = ''
        ext_id: str = ''

        if (job := self.job) and (cfat := job.cfat):
            mux = (cfat.mux_id.value) if cfat.mux_id.value else ''
            distance = cfat.distance_to_hub
            bandwidth = cfat.bandwidth
            preterm = cfat.preterm
            ext_id = cfat.ext_id

        with Vertical():
            yield Static(f"Job ID = {self.job.id.value if self.job else 'None'}")

            yield Static('MUX:')
            yield SmartInput(
                label='Mux:',
                types=[
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ],
                id='mux',
                value=mux,
                placeholder='Mux by id',
            )

            yield Static('DISTANCE TO HUB:')
            yield SmartInput(
                label='Distance:',
                id='distance_to_hub',
                value=str(distance),
                placeholder='Enter the discance from hub to endsite',
                type='number',
                types=[
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ],
            )
            yield Static('BANDWIDTH:')
            yield SmartInput(
                label='Bandwidth:',
                id='bandwidth',
                value=str(bandwidth),
                placeholder='Enter the bandwidth required',
                type='number',
                types=[
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ],
            )
            yield Static('PRETERM:')
            yield SmartInput(
                label='Preterm:',
                id='preterm',
                value=preterm,
                placeholder='Enter the preterm',
                types=[
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ],
            )
            yield Static('EXT_ID:')
            yield SmartInput(
                label='EXT_ID:',
                id='ext_id',
                value=ext_id,
                placeholder='Enter the ext_id from EP',
                types=[
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ],
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
