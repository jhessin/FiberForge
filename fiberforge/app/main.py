from textual.app import App, ComposeResult
from textual.widgets import Header, Footer


class FiberForge(App):

    TITLE = "FiberForge"
    SUB_TITLE = "Forge your fiber."
    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("q", "request_quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_request_quit(self):
        # TODO: Prompt to save before quitting.
        self.exit()


def app():
    return FiberForge()
