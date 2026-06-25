from typing import Any, Optional

from textual import log, on, work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import Screen
from textual.widgets import Footer, ListView

from fiberforge.app.screens.job_screen import JobScreen
from fiberforge.models import TimeClock
from fiberforge.models.ids import JobId
from fiberforge.persistence import Database

from .messages import UpdateDB, UpdateDetail
from .panels.details import Details
from .panels.job_details import JobDetails
from .panels.job_list import JobItem, JobList
from .panels.run_list import RunList
from .screens.quit_screen import QuitScreen
from .widgets.custom_header import Header


class MainScreen(Screen):
    BINDINGS = [
        ('q', 'request_quit', 'Quit'),
    ]
    time_clock: reactive[Optional[TimeClock]] = reactive(None, recompose=True)
    jobs: reactive[tuple[JobId, ...]] = reactive(tuple(), recompose=True)

    def on_mount(self):
        with Database() as db:
            self.time_clock = db.clock.today()
            self.jobs = tuple(db.jobs.load())

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True).data_bind(MainScreen.time_clock)
        yield Footer()

        with Horizontal():
            yield JobList().data_bind(MainScreen.time_clock, MainScreen.jobs)
            with Vertical():
                yield JobDetails()
                yield RunList()
            yield Details()

    @on(UpdateDB)
    def update_db(self, _: Any = None):
        with Database() as db:
            self.time_clock = db.clock.today()
            self.jobs = db.jobs.load()

    @on(UpdateDetail)
    async def update_detail(self, update: UpdateDetail):
        self.query_one(Details).set_widget(update.widget)

    @on(JobScreen.NewJob)
    async def new_job(self, new_job: JobScreen.NewJob):
        job = new_job.job
        if job:
            log(f'New Job created {job}')
            with Database() as db:
                db.jobs.save(job)
                if self.time_clock:
                    db.clock.save(self.time_clock.clock_in(job.id))
                else:
                    db.clock.save(db.clock.today().clock_in(job.id))
            self.update_db()

    @work
    async def action_request_quit(self):
        quiting = await self.app.push_screen_wait('quit')
        if quiting:
            self.app.exit()

    async def on_list_view_selected(self, selected: ListView.Selected):
        if isinstance(selected.item, JobItem):
            job_details = self.query_one(JobDetails)
            job_details.job = selected.item.job
            job_details.focus()


class FiberForge(App):
    TITLE = 'FiberForge'
    SUB_TITLE = 'Forge your fiber.'
    SCREENS = {
        'main': MainScreen,
        'quit': QuitScreen,
    }
    CSS_PATH = 'style.tcss'

    async def on_mount(self) -> None:
        await self.push_screen('main')

    # This doesn't update.
    # def format_title(self, title: str, sub_title: str) -> Content:
    #     title_content = super().format_title(title, sub_title)
    #     with Database() as db:
    #         clock: TimeClock = db.clock.today()
    #         if clock.clocked_in:
    #             time_content: Content = Content.styled('Clocked In', 'green')
    #             # td = clock.time_today
    #             # time_clock = f'{int(td.total_seconds()) // 3600:02}:{
    #             #     int(td.total_seconds()) % 3600 // 60:02
    #             # }:{int(td.total_seconds()) % 60:02}'
    #             # time_content: Content = Content.styled(time_clock, 'green')
    #
    #         else:
    #             time_content: Content = Content.styled('Not clocked in', 'red')
    #     return Content.assemble(title_content, time_content)


def app():
    return FiberForge()
