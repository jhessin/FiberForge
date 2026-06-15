from dataclasses import dataclass
from textual.widgets import ListView, ListItem, Label
from textual.message import Message

from fiberforge.models import Job, JobId


class JobItem(ListItem):
    pass


class JobList(ListView):

    @dataclass
    class JobSelected(Message):
        job: Job

    def __init__(self, jobs: dict[JobId, Job], **kwargs):
        super().__init__(**kwargs)
        # Preserve a stable order
        self.jobs: list[Job] = list(jobs.values())
        self.can_focus = True

    def on_mount(self) -> None:
        for job in self.jobs:
            label = job.id.value
            item = JobItem(Label(label))
            item.can_focus = True
            self.append(item)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.index
        job = self.jobs[index]
        self.post_message(self.JobSelected(job))
