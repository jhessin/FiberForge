from textual import log
from textual import work
from textual.app import ComposeResult
from textual.widgets import ListItem, Label

from fiberforge.models import Job
from fiberforge.models.ids import JobId
from fiberforge.persistence.database import Database
from .list_common import CommonList
from ..screens.job_screen import JobScreen


class JobItem(ListItem):
    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job

    def compose(self) -> ComposeResult:
        yield Label(self.job.label)
        # TODO: Add a clock-in/out button


class EmptyJobItem(ListItem):
    can_focus = False

    def __init__(self):
        super().__init__(Label('No jobs found.\nPress O to create your first Job.'))


class JobList(CommonList):
    BINDINGS = [
        ('o', 'new_job', 'Create a new job'),
        ('d', 'delete_job', 'Delete the selected job'),
    ]

    def __init__(
        self,
        *children: ListItem,
        initial_index: int | None = 0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ):
        super().__init__()
        self.has_empty: bool = False

    def on_mount(self) -> None:
        self.action_load_jobs()

    def action_load_jobs(self) -> None:
        self.clear()
        with Database() as db:
            jobs: list[JobId] = db.load_jobs()
            if not jobs:
                # Empty State
                self.append(EmptyJobItem())
                self.has_empty = True
            else:
                self.has_empty = False
                for job_id in jobs:
                    job = db.get_job_by_id(job_id.value)
                    if job:
                        item = JobItem(job)
                        item.can_focus = True
                        self.append(item)

    @work
    async def action_new_job(self):
        job = await self.app.push_screen_wait(JobScreen())
        log('JobScreen was dismissed.')
        if job:
            log(f'New Job created {job}')
            with Database() as db:
                db.save_job(job)
            self.action_load_jobs()
            # await self.recompose()

    async def action_delete_job(self):
        if self.index is not None:
            job = self.highlighted_child
            if isinstance(job, JobItem):
                with Database() as db:
                    db.delete_job(job.job.id.value)
                self.action_load_jobs()
            if len(self.children) == 0:
                self.append(EmptyJobItem())
                self.has_empty = True
