from dataclasses import dataclass

from textual.message import Message
from textual.widgets import DataTable


class VimTable(DataTable):
    BINDINGS = [
        ('j', 'cursor_down'),
        ('k', 'cursor_up'),
        ('h', 'cursor_left'),
        ('l', 'cursor_right'),
        ('d', 'cursor_delete'),
    ]

    @dataclass
    class DeleteRow(Message):
        id: str
        value: str

    def action_cursor_delete(self):
        cell_index = self.cursor_coordinate
        cell_key = self.coordinate_to_cell_key(cell_index)
        row_key = cell_key.row_key
        if row_key is not None:
            self.remove_row(row_key)
            if self.id and row_key.value:
                self.post_message(self.DeleteRow(self.id, row_key.value))
