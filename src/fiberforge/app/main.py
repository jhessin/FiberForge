from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer
from textual.screen import Screen

from fiberforge.app.panels.details import Details
from fiberforge.app.panels.job_details import JobDetails
from fiberforge.app.panels.run_list import RunList

from .screens.quit_screen import QuitScreen
from .panels.job_list import JobList


class MainScreen(Screen):
    BINDINGS = [
        ("q", "request_quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

        with Horizontal():
            yield JobList()
            with Vertical():
                yield JobDetails()
                yield RunList()
            yield Details()

    @work
    async def action_request_quit(self):
        quiting = await self.app.push_screen_wait("quit")
        if quiting:
            self.app.exit()


class FiberForge(App):

    TITLE = "FiberForge"
    SUB_TITLE = "Forge your fiber."
    SCREENS = {
        "main": MainScreen,
        "quit": QuitScreen,
    }
    CSS_PATH = "style.tcss"

    async def on_mount(self) -> None:
        await self.push_screen("main")


def app():
    return FiberForge()
