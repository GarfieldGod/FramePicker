import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap

class UiUtils:
    @staticmethod
    def show_frame(frame_label, frame):
        if frame is None: return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)

        scaled_image = qt_image.scaled(
            frame_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        frame_label.setPixmap(QPixmap.fromImage(scaled_image))