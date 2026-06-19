# fiberforge/app/views/run_list.py
from textual.widgets import ListView, ListItem, Label
from textual.message import Message
from textual import log

from fiberforge.models import FiberRun


class RunItem(ListItem):
    pass


class RunList(ListView):
    """A list view of all the Runs"""

    BINDINGS = [
        ("j", "cursor_down", "Down"),
        ("k", "cursor_up", "Up"),
        ("l", "select_cursor", "Select"),
        ("g", "cursor_home", "Top"),
        ("G", "cursor_end", "Bottom"),
    ]

    class RunSelected(Message):
        """Holds the selected run information to pass up the chain."""

        def __init__(self, run: FiberRun) -> None:
            super().__init__()
            self.run: FiberRun = run

    def __init__(self, runs: list[FiberRun], **kwargs):
        super().__init__(**kwargs)
        self.runs: list[FiberRun] = runs
        self.can_focus = True

    def on_mount(self) -> None:
        for run in self.runs:
            item = RunItem(Label(run.job_id.value))
            item.can_focus = True
            self.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        log("ITEM_SELECTED IS CALLED")
        index = event.index
        run = self.runs[index]
        self.post_message(self.RunSelected(run))

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        index = event.list_view.index
        if index:
            run = self.runs[index]
            self.post_message(self.RunSelected(run))
