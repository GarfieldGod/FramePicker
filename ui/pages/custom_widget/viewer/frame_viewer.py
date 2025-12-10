from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QLineEdit, QHBoxLayout

from ui.utils.ui_utils import UiUtils

class FrameViewer(QWidget):
    frames = None
    collection_v = None

    def __init__(self, frame_label=None, parent=None):
        super(FrameViewer, self).__init__(parent)

        if frame_label is None:
            self.frame_label = QLabel()
        else:
            self.frame_label = frame_label

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
        self.slider_value.textEdited.connect(self.on_slider_value_changed)
        self.slider_value_max.setAlignment(Qt.AlignRight)
        self.slider_value.setEnabled(False)

        self.frame_slider.setSingleStep(1)
        self.frame_slider.setEnabled(False)
        self.frame_slider.valueChanged.connect(self.on_slider_changed)

    def init_layout(self):
        self.layout_widget = QVBoxLayout(self)
        self.layout_widget.setContentsMargins(0, 0, 0, 0)

        value_layout = QHBoxLayout()
        value_layout.addWidget(self.slider_value_min)
        value_layout.addWidget(self.slider_value)
        value_layout.addWidget(self.slider_value_max)

        self.layout_widget.addWidget(self.frame_label,1)
        self.layout_widget.addLayout(value_layout)
        self.layout_widget.addWidget(self.frame_slider)

    def update_viewer(self, index=0):

        frames_empty = self.collection_v is None or len(self.collection_v.frames) == 0
        total_frame_index = 0 if frames_empty else len(self.collection_v.frames)
        min_frame_index = 0 if frames_empty else 1
        min_frame_str = f"{min_frame_index}"
        self.frame_slider.setRange(0, total_frame_index - 1)
        self.frame_slider.setValue(min_frame_index)

        self.slider_value.setText(min_frame_str if not frames_empty else "")
        self.slider_value_min.setText(min_frame_str if not frames_empty else "")
        self.slider_value_max.setText(f"{total_frame_index}" if not frames_empty else "")

        if not frames_empty and len(self.collection_v.frames) > index >= 0:
            UiUtils.show_frame(self.frame_label, self.collection_v.frames[index])
            self.frame_slider.setValue(index)
            self.slider_value.setEnabled(True)
            self.frame_slider.setEnabled(True)
        else:
            self.frame_label.setPixmap(QPixmap())
            self.slider_value.setEnabled(False)
            self.frame_slider.setEnabled(False)

    def on_slider_changed(self, value):
        try:
            if self.collection_v is not None:
                if value < 0 or value >= len(self.collection_v.frames):
                    return
                self.slider_value.setText(f"{value + 1}")
                UiUtils.show_frame(self.frame_label, self.collection_v.frames[value])
        except Exception as e:
            print(f"Viewer Slider Change Failed: {e}")

    def on_slider_value_changed(self):
        try:
            value = int(self.slider_value.text()) - 1
            if self.collection_v is not None:
                if value < 0 or value >= len(self.collection_v.frames):
                    return
                self.frame_slider.setValue(value)
                UiUtils.show_frame(self.frame_label, self.collection_v.frames[value])
        except Exception as e:
            print(f"Viewer Slider Value Change Failed: {e}")

    def view_collection(self, collection_id, viewing_index):
        try:
            collection = CollectionManager.get_collection(collection_id)
            if collection is None: return

            self.collection_v = collection
            self.update_viewer(viewing_index)
        except Exception as e:
            print(f"Viewer View Collection Failed: {e}")

    def reset(self):
        self.collection_v = None
        self.update_viewer()