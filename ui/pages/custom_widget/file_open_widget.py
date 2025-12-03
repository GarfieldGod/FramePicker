import os
from pathlib import Path

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QLabel, QWidget, QFileDialog

from src.frame_picker import FramePicker
from ui.pages.custom_thread import DecodeThread
from ui.pages.custom_widget.custom_dialog import ProgressDialog


class FileOpenWidget(QWidget):
    frame_picker = None
    on_decode_failed = pyqtSignal(str)
    on_decode_success = pyqtSignal(list)

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
        try:
            self.decode_async(file_path)
            self.file_path_label.setText(f"{file_path}")
        except Exception as e:
            self.file_path_label.setText(f"{e}")

    def decode_sync(self, file_path):
        self.release_frame_picker()
        try:
            self.frame_picker = FramePicker(file_path)
            self.frame_picker.decode()
            frames = list(self.frame_picker.get_all_frames().values())

            self.on_decode_success.emit(frames)
        except Exception as e:
            self.on_decode_failed.emit(f"Open File Failed {e}")

    def decode_async(self, file_path):
        self.release_frame_picker()
        try:
            self.frame_picker = FramePicker(file_path)
            self.prg = ProgressDialog(
                f"Decode {Path(file_path).name}:",
                min(self.frame_picker.total_frame, self.frame_picker.decode_frame_max_limit),
                operation="Decode Frame",
                auto_close=True,
                show_error=False
            )

            self.thread = DecodeThread(
                frame_picker=self.frame_picker
            )

            self.thread.decode_one_finished.connect(
                self.prg.one_finished,
                Qt.QueuedConnection
            )
            self.thread.decode_all_finished.connect(
                self.prg.all_finished,
                Qt.QueuedConnection
            )
            self.thread.decode_all_finished.connect(
                self.on_async_decode_finished,
                Qt.QueuedConnection
            )
            self.thread.start()
            self.prg.exec_()
            print(6)

        except Exception as e:
            self.on_decode_failed.emit(f"Open File Failed {e}")

    def on_async_decode_finished(self, success, ret):
        frames = list(self.frame_picker.get_all_frames().values())
        if not success:
            self.on_decode_failed.emit(f"Open File Failed {ret}")
            return

        self.on_decode_success.emit(frames)

    def release_frame_picker(self):
        if self.frame_picker is not None:
            self.frame_picker.release()
            self.frame_picker = None