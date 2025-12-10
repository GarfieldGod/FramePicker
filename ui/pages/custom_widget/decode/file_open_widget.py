from PyQt5.QtWidgets import QVBoxLayout, QLabel, QWidget

from ui.pages.custom_widget.decode.file_open_button import FileOpenButton

class FileOpenWidget(QWidget):
    def __init__(self, parent=None):
        super(FileOpenWidget, self).__init__(parent)

        self.file_path_label = QLabel("未选择有效文件")
        self.open_file_button = FileOpenButton()

        self.init_ui()

    def init_ui(self):
        layout_widget = QVBoxLayout(self)
        layout_widget.setSpacing(0)
        layout_widget.setContentsMargins(0, 0, 0, 0)

        self.file_path_label.setWordWrap(True)

        layout_open_file = QVBoxLayout()
        layout_open_file.addWidget(self.file_path_label)
        layout_open_file.addWidget(self.open_file_button)

        layout_widget.addLayout(layout_open_file)