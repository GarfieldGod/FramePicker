from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QListWidget

from ui.pages.custom_widget.file_open_widget import FileOpenWidget
from ui.pages.custom_widget.frame_viewer import FrameViewer
from ui.template.ui_page import PageContent, Container

class FrameSelectorPage(PageContent):
    show_grid = True
    def __init__(self, y, x):
        super(FrameSelectorPage, self).__init__(y, x)

    def init_container(self):

        sel = FrameSelectorContainer(4, 6)
        self.add_container(sel, 0,0)

        file = FileSelectorContainer(1,1)
        self.add_container(file, 0,4)

        file.widget_file_open.on_file_open.connect(
            sel.widget_frame_viewer.open_file
        )

class FrameSelectorContainer(Container):
    def __init__(self, x, y):
        super(FrameSelectorContainer, self).__init__(x, y)
        self.widget_frame_viewer = FrameViewer()

        self.init_ui_layout()

    def init_ui_layout(self):
        group_picker = QGroupBox(f"Frame Selector")
        layout_picker = QVBoxLayout(group_picker)

        layout_picker.addWidget(self.widget_frame_viewer)

        layout_container = QHBoxLayout(self)
        layout_container.addWidget(group_picker)

    def open_file(self, file_path):
        self.widget_frame_viewer.open_file(file_path)

class FileSelectorContainer(Container):
    def __init__(self, x, y):
        super(FileSelectorContainer, self).__init__(x, y)
        self.widget_file_open = FileOpenWidget()
        self.init_ui_layout()

    def init_ui_layout(self):
        group_picker = QGroupBox(f"Open")
        layout_picker = QVBoxLayout(group_picker)

        label_info = QLabel("Open File Here.")
        layout_picker.addWidget(label_info)

        layout_picker.addWidget(self.widget_file_open)

        layout_container = QHBoxLayout(self)
        layout_container.addWidget(group_picker)