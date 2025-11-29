import os

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget, QFileDialog


class FileOpenWidget(QWidget):
    on_file_open = pyqtSignal(str)

    def __init__(self, data_manager, parent=None):
        super(FileOpenWidget, self).__init__(parent)

        self.file_path_label = QLabel("未选择有效文件")
        self.open_file_button = QPushButton("Open File")

        self.init_ui()

    def init_ui(self):
        layout_widget = QVBoxLayout(self)
        layout_widget.setContentsMargins(0, 0, 0, 0)

        self.file_path_label.setWordWrap(True)

        layout_open_file = QVBoxLayout()
        layout_open_file.addWidget(self.file_path_label)
        layout_open_file.addWidget(self.open_file_button)
        self.open_file_button.clicked.connect(self.open_file_dialog)

        layout_widget.addLayout(layout_open_file)

    def open_file_dialog(self):
        file_path, file_type = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            ".",  # 默认打开当前目录
            "文本文件 (*.mp4);;所有文件 (*.*)"  # 过滤文件类型
        )

        if not file_path or not os.path.exists(file_path):
            return

        print(f"{file_path}")
        self.file_path_label.setText(f"{file_path}")
        self.on_file_open.emit(file_path)

    def file_invalid(self, e):
        self.file_path_label.setText(f"{e}")