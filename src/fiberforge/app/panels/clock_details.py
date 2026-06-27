import re
from datetime import datetime

from textual import on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Button, Input, Static

from fiberforge.app.messages import UpdateDB
from fiberforge.models.time_clock import TimeClock, TimeSpan
from fiberforge.persistence.database import Database


class CommandLine(Static):
    """
    This will contain an input that will accept commands to modify the associated span.
    """

    def __init__(self, span: TimeSpan) -> None:
        super().__init__()
        self.span: TimeSpan = span

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Button('🗑️', id='delete')
            yield Input()
            yield Static(id='output')

    @on(Button.Pressed, '#delete')
    def delete_time(self, event: Button.Pressed):
        with Database() as db:
            db.clock.delete(self.span)
        self.post_message(UpdateDB())
        event.stop()

    @on(Input.Submitted)
    def process_cmd(self, cmd: Input.Submitted):
        original_start = self.span.start
        COMMAND_RE = re.compile(r'^(start|end)=(.+)$')
        m = COMMAND_RE.match(cmd.input.value)
        if not m:
            self.query_one('#output', Static).update('Invalid input')
            cmd.input.value = ''
            return
        key, value = m.groups()
        with Database() as db:
            match key:
                case 'start':
                    new_span = TimeSpan(
                        start=datetime.fromisoformat(value),
                        job_id=self.span.job_id,
                        end=self.span.end,
                    )
                    db.clock.update(original_start, new_span)
                    self.query_one('#output', Static).update(
                        f'New start time updated to {new_span.start.isoformat()}'
                    )
                    cmd.input.value = ''
                case 'end':
                    new_span = TimeSpan(
                        start=self.span.start,
                        job_id=self.span.job_id,
                        end=datetime.fromisoformat(value),
                    )
                    db.clock.update(original_start, new_span)
                    self.query_one('#output', Static).update(
                        f'New end time updated to {
                            new_span.end.isoformat() if new_span.end else None
                        }'
                    )
                    cmd.input.value = ''
        self.post_message(UpdateDB())


class ClockDetails(Static):
    clock: reactive[TimeClock | None] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        if self.clock:
            for span in self.clock.time_spans:
                yield Static(f"""
                [b]{span.job_id}[/b]
                start: {span.start.isoformat()}
                end: {span.end.isoformat() if span.end else 'open'}
                """)
                yield CommandLine(span)
