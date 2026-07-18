from textual.widgets import DataTable


class VimTable(DataTable):
    BINDINGS = [
        ('j', 'cursor_down'),
        ('k', 'cursor_up'),
        ('h', 'cursor_left'),
        ('l', 'cursor_right'),
        ('d', 'cursor_delete'),
    ]
