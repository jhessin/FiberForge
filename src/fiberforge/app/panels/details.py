from textual.widget import Widget
from textual.widgets import Static


class Details(Static):
    def set_widget(self, w: Widget):
        self.remove_children()
        self.mount(w)
