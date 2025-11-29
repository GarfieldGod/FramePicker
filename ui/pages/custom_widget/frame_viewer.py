import os

import cv2
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QFileDialog, QPushButton, QLineEdit, QHBoxLayout, \
    QSizePolicy

from src.frame_picker import FramePicker
from ui.utils.ui_utils import UiUtils


class FrameViewer(QWidget):
    frame_picker = None
    frames = None

    on_decode_failed = pyqtSignal(str)

    def __init__(self, data_manager, parent=None):
        super(FrameViewer, self).__init__(parent)

        self.frame_label = QLabel()

        self.slider_value_max = QLabel()
        self.slider_value_min = QLabel()
        self.slider_value = QLineEdit()

        self.frame_slider = QSlider(Qt.Horizontal)

        self.init_ui()
        self.init_layout()

    def init_ui(self):
        self.frame_label.setStyleSheet("border: 1px solid #ccc;")
        self.frame_label.setAlignment(Qt.AlignCenter)

        self.slider_value.setAlignment(Qt.AlignCenter)
        self.slider_value.setFixedWidth(100)
        self.slider_value_max.setAlignment(Qt.AlignRight)

        self.frame_slider.setSingleStep(1)
        self.frame_slider.valueChanged.connect(self.on_slider_changed)

    def init_layout(self):
        layout_widget = QVBoxLayout(self)
        layout_widget.setContentsMargins(0, 0, 0, 0)

        value_layout = QHBoxLayout()
        value_layout.addWidget(self.slider_value_min)
        value_layout.addWidget(self.slider_value)
        value_layout.addWidget(self.slider_value_max)

        layout_widget.addWidget(self.frame_label,1)
        layout_widget.addLayout(value_layout)
        layout_widget.addWidget(self.frame_slider)

    def set_total_frame(self, total_frame):
        self.frame_slider.setRange(0, total_frame)
        self.slider_value.setText("0")
        self.slider_value_min.setText("0")
        self.slider_value_max.setText(f"{total_frame}")

    def open_file(self, file_path):
        self.release_frame_picker()
        try:
            self.frame_picker = FramePicker(file_path)

            UiUtils.show_frame(self.frame_label, self.frame_picker.frist_frame)
            self.set_total_frame(self.frame_picker.total_frame)

            self.frame_picker.decode()
            self.frames = self.frame_picker.get_all_frames()
        except Exception as e:
            self.on_decode_failed.emit(f"Open File Failed {e}")

    def release_frame_picker(self):
        if self.frame_picker is not None:
            self.frame_picker.release()
            self.frame_picker = None

    def on_slider_changed(self, value):
        try:
            if self.frames is not None:
                if value < 0 or value >= len(self.frames):
                    return
                self.slider_value.setText(f"{value}")
                UiUtils.show_frame(self.frame_label, self.frames[value])
                print(f"on_slider_changed {value}")
        except Exception as e:
            print(e)