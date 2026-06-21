from textual import log, on, work
from textual.app import ComposeResult
from textual.containers import HorizontalGroup
from textual.widgets import Button, Label, ListItem

from fiberforge.models import Job
from fiberforge.models.ids import JobId
from fiberforge.persistence.database import Database

from ..screens.job_screen import JobScreen
from .list_common import CommonList


class JobItem(ListItem):
    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job

    def compose(self) -> ComposeResult:
        with Database() as db:
            clock = db.load_todays_clock()
            with HorizontalGroup():
                yield Label(self.job.label)
                yield Button(
                    'Clock Out' if clock.is_clocked_in(self.job.id) else 'Clock In',
                    variant='error' if clock.is_clocked_in(self.job.id) else 'default',
                )

    @on(Button.Pressed)
    async def clock_in_or_out(self, _: Button.Pressed) -> None:
        with Database() as db:
            clock = db.load_todays_clock()
            if clock.is_clocked_in(self.job.id):
                log.event('CLOCKING OUT')
                clock = clock.clock_out()
            else:
                log.event('CLOCKING IN')
                clock = clock.clock_in(self.job.id)
            db.save_clock(clock)
        await self.recompose()


class EmptyJobItem(ListItem):
    can_focus = False

    def __init__(self):
        super().__init__(Label('No jobs found.\nPress O to create your first Job.'))


class JobList(CommonList):
    BINDINGS = [
        ('o', 'new_job', 'Create a new job'),
        ('d', 'delete_job', 'Delete the selected job'),
    ]

    def __init__(self):
        super().__init__()
        self.has_empty: bool = False

    def on_mount(self) -> None:
        self.action_load_jobs()

    def action_load_jobs(self) -> None:
        self.clear()
        with Database() as db:
            jobs: list[JobId] = db.load_todays_jobs()
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
                clock = db.load_todays_clock().clock_in(job.id)
                db.save_clock(clock)
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
