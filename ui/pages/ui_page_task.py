from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QListWidget

from ui.template.ui_page import PageContent, Container

class FrameSelectorPage(PageContent):
    # show_grid = True
    def __init__(self, y, x):
        super(FrameSelectorPage, self).__init__(y, x)

    def init_container(self):
        task = FrameSelectorContainer(6, 6)
        self.add_container(task, 0,0)

class FrameSelectorContainer(Container):
    def __init__(self, x, y):
        super(FrameSelectorContainer, self).__init__(x, y)

        self.init_ui_layout()

    def init_ui_layout(self):
        group_picker = QGroupBox(f"Frame Picker")
        layout_picker = QVBoxLayout(group_picker)

        label_info = QLabel("This is the Frame Picker Page.")
        layout_picker.addWidget(label_info)

        layout_container = QHBoxLayout(self)
        layout_container.addWidget(group_picker)