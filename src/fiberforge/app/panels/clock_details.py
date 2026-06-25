from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widgets import Static

from fiberforge.models.time_clock import TimeClock


class CommandLine(Static):
    """
    This will contain an input that will accept commands to modify the associated span.
    """


class ClockDetails(Static):
    clock: reactive[TimeClock | None] = reactive(None, recompose=True)

    def compose(self) -> ComposeResult:
        if self.clock:
            for span in self.clock.time_spans:
                yield Static(f"""
                [b]{span.job_id}[/b]
                start: {span.start.ctime()}
                end: {span.end.ctime() if span.end else 'open'}
                """)
