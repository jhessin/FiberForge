from textual import work
from textual.app import ComposeResult

from platformdirs import PlatformDirs
from textual.widgets import ListItem, Label
from textual import log

from fiberforge.app.screens.job_screen import JobScreen

from .list_common import CommonList

from fiberforge.models import Job
from fiberforge.models.ids import JobId
from fiberforge.persistence.sqlite_repo import Store

dirs = PlatformDirs("FiberForge", "GrillbrickStudios")
data_dir = dirs.user_data_path


class JobItem(ListItem):

    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job

    def compose(self) -> ComposeResult:
        yield Label(self.job.id.value)


class EmptyJobItem(ListItem):
    can_focus = False

    def __init__(self):
        super().__init__(Label("No jobs found.\nPress O to create your first Job."))


class JobList(CommonList):
    BINDINGS = [
        ("o", "new_job", "Create a new job"),
        ("d", "delete_job", "Delete the selected job"),
    ]

    def on_mount(self) -> None:
        repo: Store = Store(data_dir)
        db: list[JobId] = repo.load_jobs()
        if not db:
            # Empty State
            self.append(EmptyJobItem())
            self.has_empty = True
        else:
            self.has_empty = False
            for job_id in db:
                job = repo.get_job_by_id(job_id.value)
                if job:
                    item = JobItem(job)
                    item.can_focus = True
                    self.append(item)
        repo.close()

    @work
    async def action_new_job(self):
        job = await self.app.push_screen_wait(JobScreen())
        log("JobScreen was dismissed.")
        if job:
            log(f"New Job created {job}")
            repo: Store = Store(data_dir)
            repo.save_job(job)
            repo.close()
            if self.has_empty:
                await self.clear()
                self.has_empty = False
            self.append(JobItem(job))
            # await self.recompose()

    async def action_delete_job(self):
        if self.index is not None:
            job = await self.pop(self.index)
            if isinstance(job, JobItem):
                store = Store(data_dir)
                store.delete_job(job.job.id.value)
                store.close()
            if len(self.children) == 0:
                self.append(EmptyJobItem())
                self.has_empty = True
