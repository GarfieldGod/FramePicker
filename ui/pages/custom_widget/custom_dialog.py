import os.path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QComboBox, \
    QWidget, QLabel, QProgressBar, QScrollArea

from ui.template.ui_dialog import Dialog


class DownLoadFrameDialog(Dialog):
    download_format = ["png", "jpeg"]

    def __init__(self, collection_name, parent=None):
        self.file_path = QLineEdit(os.path.join(os.path.abspath("."), "output", collection_name))
        self.file_name = QLineEdit("default")
        self.file_format = QComboBox()
        self.file_format.addItems(self.download_format)

        super().__init__(title_text="DownLoad Frame:", parent=parent)


    def init_content_widget(self):
        self.content = QWidget()
        layout_content = QVBoxLayout(self.content)

        layout_content.addWidget(QLabel("Output Path:"))
        layout_content.addWidget(self.file_path)
        layout_content.addWidget(QLabel("File Name:"))
        layout_content.addWidget(self.file_name)
        layout_content.addWidget(QLabel("File Format:"))
        layout_content.addWidget(self.file_format)

    def values(self):
        return self.file_path.text(), self.file_name.text(), self.file_format.currentText()

class ProgressDialog(Dialog):
    current_value = 0

    def __init__(self, title, total, operation="", auto_close=False, show_error=True, parent=None):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.progress_label = QLabel(f"0/{total}")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_area = QScrollArea()
        self.error_area.setWidgetResizable(True)
        self.error_area.hide()
        self.error_widget = QWidget()
        self.error_layout = QVBoxLayout(self.error_widget)
        self.error_area.setWidget(self.error_widget)

        self.total_value = total
        self.operation = operation
        self.auto_close = auto_close
        self.show_error = show_error
        super().__init__(title_text=title, show_cancel_button=False, show_confirm_button=False, parent=parent)


    def init_content_widget(self):
        self.content = QWidget()
        self.layout_content = QVBoxLayout(self.content)

        self.layout_content.addWidget(self.progress_label)
        self.layout_content.addWidget(self.progress_bar)
        self.layout_content.addWidget(self.error_area)

    def one_finished(self, success, ret):
        self.current_value += 1
        self.progress_bar.setValue(self.current_value)
        self.progress_label.setText(f"{self.operation}: {int(self.current_value/self.total_value * 100)}% ({self.current_value}/{self.total_value})")
        if not success:
            self.error_area.show()
            self.error_layout.addWidget(QLabel(f"{self.operation}: {self.current_value} Failed{f":\nError: {ret}" if self.show_error else ""}"))

    def all_finished(self, success, ret):
        self.current_value = 0
        ret_info = QLabel(f"{self.operation} {f"Failed:\nError: {ret}" if not success else "Success"}")
        ret_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_content.addWidget(ret_info)
        if success and self.auto_close:
            self.close()
        self.show_confirm_button()