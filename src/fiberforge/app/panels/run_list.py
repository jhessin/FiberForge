from .list_common import CommonList


class RunList(CommonList):

    def __init__(self) -> None:
        super().__init__()
        self.can_focus = False
