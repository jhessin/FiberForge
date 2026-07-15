from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Static

from fiberforge.app.widgets.smart_input import SmartInput
from fiberforge.models.job import Job

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
        segment: str = ''

        if (job := self.job) and (network := job.network):
            segment = network.segment if network.segment else ''

        with Vertical():
            yield Static(f"Job ID = {self.job.id.value if self.job else 'None'}")

            yield DataTable(id='node_list')
            # yield Static('NODES:')
            # for node in node_list:
            #     yield node
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

            yield DataTable(id='hub_list')
            # yield Static('HUBS:')
            # for hub in hub_list:
            #     yield hub
            yield SmartInput(
                label='Hub',
                id='hubs',
                placeholder='Add a hub',
            )

            yield DataTable(id='endsite_list')
            # yield Static('ENDSITES:')
            # for endsite in endsite_list:
            #     yield endsite
            yield SmartInput(
                label='Endsite',
                id='endsites',
                placeholder='Add an endsite',
            )

            yield DataTable(id='removing_list')
            # yield Static('REMOVING:')
            # for removing in removing_list:
            #     yield removing
            yield SmartInput(
                label='Removing',
                id='removing',
                placeholder='Remove a device by id',
            )
            with Horizontal():
                yield Button('Save', id='save', variant='primary')
                yield Button('Cancel', id='cancel', variant='error')

    def on_mount(self):
        """
        Use a Select widget for the Enums
        Use a DataTable for lists.
        REMINDER - Use a Tree for Runs
        """
        node_list: list[str] = []
        hub_list: list[str] = []
        endsite_list: list[str] = []
        removing_list: list[str] = []

        if (job := self.job) and (network := job.network):
            node_list = [node for node in network.nodes]
            hub_list = [hub for hub in network.hubs]
            endsite_list = [endsite.value for endsite in network.endsites]
            removing_list = [id.value for id in network.removing]

        for table in self.query_children(DataTable):
            table.cursor_type = 'row'
            match table.id:
                case 'node_list':
                    table.add_column('Nodes')
                    table.add_rows(node_list)
                case 'hub_list':
                    table.add_column('Hubs')
                    table.add_rows(hub_list)
                case 'endsite_list':
                    table.add_column('Endsites')
                    table.add_rows(endsite_list)
                case 'removing_list':
                    table.add_column('Removing')
                    table.add_rows(removing_list)

    @on(Input.Submitted)
    @on(Button.Pressed, '#save')
    def save(self, data: Input.Submitted | Button.Pressed):
        """TODO: parse the information from the submitted field, or from all
        fields if the type of data is Button.Pressed."""

    @on(Button.Pressed, '#cancel')
    def action_cancel(self):
        self.remove()
