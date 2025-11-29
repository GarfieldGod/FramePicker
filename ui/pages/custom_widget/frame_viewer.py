import os

import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QFileDialog, QPushButton

from src.frame_picker import FramePicker


class FrameViewer(QWidget):
    frame_picker = None
    frames = None

    def __init__(self, parent=None):
        super(FrameViewer, self).__init__(parent)

        self.frame_label = QLabel()

        self.slider_value = QLabel("total_frames")
        self.frame_slider = QSlider(Qt.Horizontal)

        self.init_ui()

    def init_ui(self):
        layout_widget = QVBoxLayout(self)
        layout_widget.setContentsMargins(0, 0, 0, 0)

        self.frame_label.setStyleSheet("border: 1px solid #ccc;")
        self.frame_label.setAlignment(Qt.AlignCenter)

        self.frame_slider.setSingleStep(1)
        self.frame_slider.valueChanged.connect(self.on_slider_changed)

        layout_widget.addWidget(self.frame_label,1)
        layout_widget.addWidget(self.slider_value)
        layout_widget.addWidget(self.frame_slider)

    def set_total_frame(self, total_frame):
        self.frame_slider.setRange(0, total_frame)

    def open_file(self, file_path):
        if self.frame_picker is not None:
            self.frame_picker.release()
            self.frame_picker = None
        try:
            self.frame_picker = FramePicker(file_path)
            self.show_frame(self.frame_picker.frist_frame)
            self.set_total_frame(self.frame_picker.total_frame)
            self.frame_picker.decode()
            self.frames = self.frame_picker.get_all_frames()
        except Exception as e:
            print(e)

    def on_slider_changed(self, value):
        try:
            if self.frames is not None:
                if value < 0 or value >= len(self.frames):
                    return
                self.slider_value.setText(f"{value}")
                self.show_frame(self.frames[value])
                print(f"on_slider_changed {value}")
        except Exception as e:
            print(e)

    def show_frame(self, frame):
        if frame is None: return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        scaled_image = qt_image.scaled(
            self.frame_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.frame_label.setPixmap(QPixmap.fromImage(scaled_image))