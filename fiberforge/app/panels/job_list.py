from textual import work
from textual.app import ComposeResult

from platformdirs import PlatformDirs
from textual.widgets import ListItem, Label
from textual import log

from fiberforge.app.screens.job_screen import JobScreen

from .list_common import CommonList

from fiberforge.models import Job
from fiberforge.models.ids import JobId
from fiberforge.persistence.json_repo import JsonRepository


class JobItem(ListItem):

    def __init__(self, job: Job) -> None:
        super().__init__()
        self.job = job

    def compose(self) -> ComposeResult:
        yield Label(self.job.id.value)


class EmptyJobItem(ListItem):
    can_focus = False

    def __init__(self):
        super().__init__(Label("No jobs found.\nPress N to create your first Job."))


class JobList(CommonList):
    BINDINGS = [
        ("n", "new_job", "Create a new job"),
    ]

    def on_mount(self) -> None:
        dirs = PlatformDirs("FiberForge", "GrillbrickStudios")
        data_dir = dirs.user_data_path
        repo = JsonRepository(data_dir)
        db: dict[JobId, Job] = repo.load_jobs()
        if not db:
            # Empty State
            self.append(EmptyJobItem())
            self.has_empty = True
        else:
            for _, job in db.items():
                item = JobItem(job)
                item.can_focus = True
                self.append(item)

    @work
    async def action_new_job(self):
        job = await self.app.push_screen_wait(JobScreen())
        log("JobScreen was dismissed.")
        if job:
            log(f"New Job created {job}")
            if self.has_empty:
                await self.clear()
                self.has_empty = False
            self.append(JobItem(job))
            # await self.recompose()
