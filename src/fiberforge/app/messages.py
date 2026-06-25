from dataclasses import dataclass

from textual.message import Message
from textual.widget import Widget


class UpdateDB(Message):
    pass


@dataclass
class UpdateDetail(Message):
    widget: Widget
