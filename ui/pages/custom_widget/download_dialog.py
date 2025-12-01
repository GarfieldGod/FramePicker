import os.path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QComboBox, \
    QWidget, QLabel, QProgressBar

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
    download_frame_count = 0

    def __init__(self, collection_name, frame_count, parent=None):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, frame_count)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.progress_label = QLabel(f"0/{frame_count}")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_layout = QVBoxLayout()

        self.frame_count = frame_count
        super().__init__(title_text=f"DownLoad {collection_name}:", show_cancel_button=False, show_confirm_button=False, parent=parent)


    def init_content_widget(self):
        self.content = QWidget()
        layout_content = QVBoxLayout(self.content)

        layout_content.addWidget(self.progress_label)
        layout_content.addWidget(self.progress_bar)
        layout_content.addLayout(self.error_layout)

    def on_download_one_finished(self, success, ret):
        self.download_frame_count += 1
        self.progress_bar.setValue(self.download_frame_count)
        self.progress_label.setText(f"Downloaded: {int(self.download_frame_count/self.frame_count * 100)}% ({self.download_frame_count}/{self.frame_count})")
        if not success:
            self.error_layout.addWidget(QLabel(f"Download Frame: {self.download_frame_count} Failed:\nError: {ret}"))

    def on_download_all_finished(self, success, ret):
        self.download_frame_count = 0
        print(f"下载全部完成！整体状态：{'成功' if success else '失败'}，信息：{ret}")
        if not success:
            self.error_layout.addWidget(QLabel(f"Download {f"Failed:\nError: {ret}" if not success else "Success"}"))
        self.show_confirm_button()