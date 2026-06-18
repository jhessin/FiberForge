from fiberforge.app.panels.list_common import CommonList


class RunList(CommonList):
    DEFAULT_CSS = """
RunList {
    border: tall aqua;
    width: 1fr;
    height: 50%;
    margin: 2 2;
}
    """

    def __init__(self) -> None:
        super().__init__()
        self.can_focus = False
