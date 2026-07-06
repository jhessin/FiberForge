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


class NetworkScreen(Widget):
    BINDINGS = [
        ('enter', 'submit', 'Save Network'),
        ('escape', 'cancel', 'Cancel'),
    ]

    job: reactive[Optional[Job]] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        """Compose the component here."""
        # Front load all the listed items
        node_list: list[SmartInput] = []
        segment: str = ''
        hub_list: list[SmartInput] = []
        endsite_list: list[SmartInput] = []
        removing_list: list[SmartInput] = []

        if (job := self.job) and (network := job.network):
            node_list = [
                SmartInput(
                    label=str(i),
                    id=f'node{i}',
                    value=network.nodes[i],
                    types=[
                        SmartInput.Type.Input,
                        SmartInput.Type.Output,
                        SmartInput.Type.Delete,
                    ],
                )
                for i in range(len(network.nodes))
            ]
            segment = network.segment if network.segment else ''
            hub_list = [
                SmartInput(
                    label=str(i),
                    id=f'hub{i}',
                    value=network.hubs[i],
                    types=[
                        SmartInput.Type.Input,
                        SmartInput.Type.Output,
                        SmartInput.Type.Delete,
                    ],
                )
                for i in range(len(network.hubs))
            ]
            endsite_list = [
                SmartInput(
                    label=str(i),
                    id=f'endsite{i}',
                    value=network.endsites[i],
                    types=[
                        SmartInput.Type.Input,
                        SmartInput.Type.Output,
                        SmartInput.Type.Delete,
                    ],
                )
                for i in range(len(network.endsites))
            ]
            removing_list = [
                SmartInput(
                    label=str(i),
                    id=f'removing{i}',
                    value=network.removing[i],
                    types=[
                        SmartInput.Type.Input,
                        SmartInput.Type.Output,
                        SmartInput.Type.Delete,
                    ],
                )
                for i in range(len(network.removing))
            ]

        with Vertical():
            yield Static(f"Job ID = {self.job.id.value if self.job else 'None'}")

            yield Static('NODES:')
            for node in node_list:
                yield node
            yield SmartInput(
                label='Node',
                id='nodes',
                placeholder='Add a node',
            )

            yield Static('SEGMENT:')
            yield SmartInput(
                label='Segment',
                value=segment,
                id='segment',
                placeholder='Enter segment name',
                types=[
                    SmartInput.Type.Input,
                    SmartInput.Type.Output,
                ],
            )

            yield Static('HUBS:')
            for hub in hub_list:
                yield hub
            yield SmartInput(
                label='Hub',
                id='hubs',
                placeholder='Add a hub',
            )

            yield Static('ENDSITES:')
            for endsite in endsite_list:
                yield endsite
            yield SmartInput(
                label='Endsite',
                id='endsites',
                placeholder='Add an endsite',
            )

            yield Static('REMOVING:')
            for removing in removing_list:
                yield removing
            yield SmartInput(
                label='Removing',
                id='removing',
                placeholder='Remove a device by id',
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
