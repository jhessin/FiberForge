from textual.widgets import ListView


class CommonList(ListView):
    DEFAULT_CSS = """
Screen {
    align: center middle;
}

CommonList {
    border: tall white;
    width: 1fr;
    height: 100%;
    margin: 2 2;

    &:focus {
        border: thick white;
    }
}

Label {
    padding: 1 2;
}
    """

    BINDINGS = [
        ("j", "cursor_down", "Cursor down"),
        ("k", "cursor_up", "Cursor up"),
        ("l", "select_cursor", "Select"),
    ]
