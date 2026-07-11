from typing import Optional

from textual import log, on
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.reactive import reactive
from textual.widgets import Button, Label, ListItem

from fiberforge.app.messages import UpdateDB, UpdateDetail
from fiberforge.app.screens.job_screen import JobScreen
from fiberforge.models import Job, TimeClock
from fiberforge.models.ids import JobId
from fiberforge.persistence.database import Database

from .list_common import CommonList


class JobItem(ListItem):
    time_clock: reactive[Optional[TimeClock]] = reactive(None)

    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job

    def compose(self) -> ComposeResult:
        with Database() as db:
            clock = self.time_clock or db.clock.today()
            with HorizontalGroup():
                yield Label(self.job.label)
                yield Button(
                    'Clock Out' if clock.is_clocked_in(self.job.id) else 'Clock In',
                    variant='error' if clock.is_clocked_in(self.job.id) else 'default',
                )

    @on(Button.Pressed)
    async def clock_in_or_out(self, _: Button.Pressed) -> None:
        with Database() as db:
            clock = db.clock.today()
            if clock.is_clocked_in(self.job.id):
                log.event('CLOCKING OUT')
                clock = clock.clock_out()
            else:
                log.event('CLOCKING IN')
                clock = clock.clock_in(self.job.id)
            db.clock.save(clock)

        self.post_message(UpdateDB())


class EmptyJobItem(ListItem):
    can_focus = False

    def __init__(self):
        super().__init__(Label('No jobs found.\nPress O to create your first Job.'))


class JobList(CommonList):
    BINDINGS = [
        ('d', 'delete_job', 'Delete the selected job'),
        ('o', 'new_job', 'Create a new job'),
        ('space', 'push_button', 'Clock In/Out'),
    ]
    time_clock: reactive[Optional[TimeClock]] = reactive(None)
    jobs: reactive[tuple[JobId, ...]] = reactive(())

    def __init__(self):
        super().__init__()
        self.has_empty: bool = False

    async def action_new_job(self):
        self.post_message(UpdateDetail(JobScreen()))

    def on_mount(self) -> None:
        self.post_message(UpdateDB())

    def action_push_button(self):
        item = self.highlighted_child
        if item:
            item.query_one(Button).press()

    def watch_jobs(self):
        self.clear()
        if not self.jobs:
            # Empty State
            self.append(EmptyJobItem())
            self.has_empty = True
        else:
            self.has_empty = False
            with Database() as db:
                for job_id in self.jobs:
                    job = db.jobs.by_id(job_id)
                    if job:
                        self.append(JobItem(job).data_bind(JobList.time_clock))
        self.focus()

    async def action_delete_job(self):
        if self.index is not None:
            job = self.highlighted_child
            if isinstance(job, JobItem):
                with Database() as db:
                    db.jobs.delete(job.job.id)
            if len(self.children) == 0:
                self.append(EmptyJobItem())
                self.has_empty = True
            self.post_message(UpdateDB())
