from dataclasses import dataclass
from textual.widgets import ListView, ListItem, Label
from textual.message import Message
from textual.binding import Binding

from fiberforge.models import Job, JobId


class JobItem(ListItem):
    pass


class EmptyJobItem(ListItem):
    """Non-selectable placeholder when there are no jobs."""

    can_focus = False


class JobList(ListView):

    BINDINGS = [
        Binding("n", "new_job", "New Job"),
    ]

    @dataclass
    class JobSelected(Message):
        job: Job

    def __init__(self, jobs: dict[JobId, Job], **kwargs):
        super().__init__(**kwargs)
        # Preserve a stable order
        self.jobs: list[Job] = list(jobs.values())
        self.can_focus = True

    def on_mount(self) -> None:
        if not self.jobs:
            # Empty state
            placeholder = EmptyJobItem(
                Label("No jobs found.\nPress N to create your first Job.")
            )
            self.append(placeholder)
        else:
            for job in self.jobs:
                label = job.id.value
                item = JobItem(Label(label))
                item.can_focus = True
                self.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        # Guard against empty state / placeholder
        if not self.jobs:
            return

        index = event.index
        if index < 0 or index >= len(self.jobs):
            return

        job = self.jobs[index]
        self.post_message(self.JobSelected(job))

    def action_new_job(self) -> None:
        """Open the new job screen"""
        # Let the app decide what "new job" means
        # e.g. push a JobForm screen
        # self.app.post_message(self.JobSelected(job=None))  # or a custom NewJob message
