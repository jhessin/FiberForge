from textual.widgets import ListView


class CommonList(ListView):
    BINDINGS = [
        ("j", "cursor_down", "Cursor down"),
        ("k", "cursor_up", "Cursor up"),
        ("l", "select_cursor", "Select"),
    ]
