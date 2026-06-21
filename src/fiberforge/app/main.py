from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.content import Content
from textual.screen import Screen
from textual.widgets import Footer, Header, ListView

from fiberforge.models import TimeClock
from fiberforge.persistence import Database

from .panels.details import Details
from .panels.job_details import JobDetails
from .panels.job_list import JobItem, JobList
from .panels.run_list import RunList
from .screens.quit_screen import QuitScreen


class MainScreen(Screen):
    BINDINGS = [
        ('q', 'request_quit', 'Quit'),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

        with Horizontal():
            yield JobList()
            with Vertical():
                yield JobDetails()
                yield RunList()
            yield Details()

    @work
    async def action_request_quit(self):
        quiting = await self.app.push_screen_wait('quit')
        if quiting:
            self.app.exit()

    async def on_list_view_selected(self, selected: ListView.Selected):
        if isinstance(selected.item, JobItem):
            self.query_one(JobDetails).job = selected.item.job


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

    def format_title(self, title: str, sub_title: str) -> Content:
        title_content = super().format_title(title, sub_title)
        with Database() as db:
            clock: TimeClock = db.load_todays_clock()
            if clock.clocked_in:
                td = clock.time_today
                time_clock = f'{int(td.total_seconds()) // 3600:02}:{
                    int(td.total_seconds()) % 3600 // 60:02
                }:{int(td.total_seconds()) % 60:02}'
                time_content: Content = Content.styled(time_clock, 'green')

            else:
                time_content: Content = Content.styled('Not clocked in', 'red')
        return Content.assemble(title_content, time_content)


def app():
    return FiberForge()
