from dataclasses import replace
from typing import Literal, Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.reactive import reactive
from textual.types import NoSelection
from textual.widget import Widget
from textual.widgets import Button, DataTable, Input, Select, Static

from fiberforge.app.messages import UpdateDB
from fiberforge.app.widgets.smart_input import SmartInput
from fiberforge.models.ids import DeviceId, SpanId
from fiberforge.models.job import Job, NetworkSpec
from fiberforge.persistence.database import Database


class NetworkScreen(Widget):
    BINDINGS = [
        ('enter', 'submit', 'Save Network'),
        ('escape', 'cancel', 'Cancel'),
        ('j', 'dt_down', 'Down'),
        ('k', 'dt_up', 'Up'),
        ('h', 'dt_left', 'Left'),
        ('l', 'dt_right', 'Right'),
        ('d', 'dt_delete', 'Delete'),
    ]

    job: reactive[Optional[Job]] = reactive(None)

    def compose(self) -> ComposeResult:
        """Compose the component here."""
        # Front load all the listed items
        segment: str = ''

        if (job := self.job) and (network := job.network):
            segment = network.segment if network.segment else ''

        with VerticalScroll():
            yield Static(f"Job ID = {self.job.id.value if self.job else 'None'}")

            yield DataTable(id='node_list')
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
            )

            yield DataTable(id='hub_list')
            yield SmartInput(
                label='Hub',
                id='hubs',
                placeholder='Add a hub',
            )

            yield DataTable(id='endsite_list')
            # yield Static('ENDSITES:')
            # for endsite in endsite_list:
            #     yield endsite
            yield Select[DeviceId.DeviceType](
                options=(
                    (
                        'Hub',
                        DeviceId.DeviceType.HUB,
                    ),
                    (
                        'Node',
                        DeviceId.DeviceType.NODE,
                    ),
                    (
                        'Term Panel',
                        DeviceId.DeviceType.TERM_PANEL,
                    ),
                ),
                allow_blank=False,
                value=DeviceId.DeviceType.TERM_PANEL,
                id='new_endsite_type',
            )
            yield SmartInput(
                label='Endsite',
                id='endsites',
                placeholder='Add an endsite',
            )

            yield DataTable(id='removing_list')
            # yield Static('REMOVING:')
            # for removing in removing_list:
            #     yield removing
            yield Select[DeviceId.DeviceType | Literal['Span']](
                options=(
                    ('Span', 'Span'),
                    (
                        'Can',
                        DeviceId.DeviceType.SPLICE_CAN,
                    ),
                    (
                        'Hub',
                        DeviceId.DeviceType.HUB,
                    ),
                    (
                        'Node',
                        DeviceId.DeviceType.NODE,
                    ),
                    (
                        'Term Panel',
                        DeviceId.DeviceType.TERM_PANEL,
                    ),
                ),
                allow_blank=False,
                value='Span',
                id='new_removing_type',
            )
            yield SmartInput(
                label='Removing',
                id='removing',
                placeholder='Remove a device by id',
            )
            with Horizontal():
                yield Button('Save', id='save', variant='primary')
                yield Button('Cancel', id='cancel', variant='error')

    def watch_job(self):
        """
        Use a Select widget for the Enums
        Use a DataTable for lists.
        REMINDER - Use a Tree for Runs
        """
        node_list: set[str] = set()
        hub_list: set[str] = set()
        endsite_list: set[tuple[str, str]] = set()
        removing_list: set[tuple[str, str]] = set()
        self.log.debug(f'job = {self.job}')

        if (job := self.job) and (network := job.network):
            self.log.debug(f'network = {network}')
            node_list = {node for node in network.nodes}
            hub_list = {hub for hub in network.hubs}
            endsite_list = {
                (endsite.value, str(endsite.deviceType)) for endsite in network.endsites
            }
            removing_list = {
                (
                    id.value,
                    str(id.deviceType) if isinstance(id, DeviceId) else 'Span',
                )
                for id in network.removing
            }

        for table in self.query(DataTable):
            table.cursor_type = 'row'
            table.clear(columns=True)
            match table.id:
                case 'node_list':
                    table.add_column('Nodes')
                    self.log.debug(f'Showing nodes {node_list}')
                    for row in node_list:
                        table.add_row(
                            row,
                            key=row,
                        )
                    self.log.debug(f'There should be {table.row_count} rows')
                case 'hub_list':
                    table.add_column('Hubs')
                    for row in hub_list:
                        table.add_row(
                            row,
                            key=row,
                        )
                case 'endsite_list':
                    table.add_columns('Endsites', 'type')
                    # table.add_rows(endsite_list)
                    for row, type in endsite_list:
                        table.add_row(
                            row,
                            type,
                            key=row,
                        )
                case 'removing_list':
                    table.add_columns('Removing', 'type')
                    # table.add_rows(removing_list)
                    for row, type in removing_list:
                        table.add_row(
                            row,
                            type,
                            key=row,
                        )

    @property
    def _focused_table(self) -> DataTable | None:
        widget = self.app.focused
        return widget if isinstance(widget, DataTable) else None

    def action_dt_down(self):
        if table := self._focused_table:
            table.action_cursor_down()

    def action_dt_up(self):
        if table := self._focused_table:
            table.action_cursor_up()

    def action_dt_left(self):
        if table := self._focused_table:
            table.action_cursor_left()

    def action_dt_right(self):
        if table := self._focused_table:
            table.action_cursor_right()

    def action_dt_delete(self):
        if table := self._focused_table:
            cell_index = table.cursor_coordinate
            cell_key = table.coordinate_to_cell_key(cell_index)
            row_key = cell_key.row_key
            if row_key is not None:
                table.remove_row(row_key)

    @on(Input.Submitted)
    @on(Button.Pressed, '#save')
    def save(self, data: Input.Submitted | Button.Pressed):
        """parse the information from the submitted field, or from all
        fields if the type of data is Button.Pressed."""
        assert self.job, 'Job should be set before saving'
        network: NetworkSpec = self.job.network or NetworkSpec()
        new_job: Job = self.job

        if isinstance(data, Input.Submitted):
            match data.input.id:
                case 'nodes':
                    self.log.debug(f'adding node {data.input.value}')
                    nodes = {*network.nodes, data.input.value}
                    self.log.debug(f'setting nodes {nodes}')
                    network = replace(network, nodes=tuple(nodes))
                case 'segment':
                    segment = data.input.value
                    network = replace(network, segment=segment)
                case 'hubs':
                    hubs = {*network.hubs, data.input.value}
                    network = replace(network, hubs=tuple(hubs))
                case 'endsites':
                    """Need to add a select for the device type"""
                    endsite_type: DeviceId.DeviceType | NoSelection = self.query_one(
                        '#new_endsite_type', Select
                    ).value
                    if isinstance(endsite_type, NoSelection):
                        return
                    endsites = {
                        *network.endsites,
                        DeviceId(data.input.value, deviceType=endsite_type),
                    }
                    network = replace(network, endsites=tuple(endsites))
                case 'removing':
                    """Need to add a select for the device type or span"""
                    removing_type: (
                        DeviceId.DeviceType | Literal['Span'] | NoSelection
                    ) = self.query_one('#new_removing_type', Select).value
                    if isinstance(removing_type, NoSelection):
                        return
                    if removing_type == 'Span':
                        removing = {*network.removing, SpanId(data.input.value)}
                        network = replace(network, removing=tuple(removing))
                    else:
                        removing = {
                            *network.removing,
                            DeviceId(data.input.value, removing_type),
                        }
                        network = replace(network, removing=tuple(removing))

        else:
            """Parse all inputs here"""
            pass

        new_job = replace(new_job, network=network)
        with Database() as db:
            db.jobs.save(new_job)
            self.log.debug(f'updating job with {new_job}')
        self.post_message(UpdateDB())

    @on(Button.Pressed, '#cancel')
    def action_cancel(self):
        self.remove()
