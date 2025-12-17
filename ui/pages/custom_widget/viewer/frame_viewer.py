from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QLineEdit, QHBoxLayout

from src.collection.collection_manager import CollectionManager
from ui.pages.custom_widget.viewer.functions.crop_widget import CropLabel
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

        self.max_index_label = QLabel()
        self.min_index_label = QLabel()
        self.current_index_label = QLineEdit()

        self.frame_slider = QSlider(Qt.Horizontal)

        self.init_ui()
        self.init_layout()

    def init_ui(self):
        self.frame_label.setStyleSheet("border: 1px solid #ccc;")
        self.frame_label.setAlignment(Qt.AlignCenter)

        self.current_index_label.setAlignment(Qt.AlignCenter)
        self.current_index_label.setFixedWidth(100)
        self.current_index_label.textEdited.connect(self.on_slider_value_changed)
        self.max_index_label.setAlignment(Qt.AlignRight)
        self.current_index_label.setEnabled(False)

        self.frame_slider.setSingleStep(1)
        self.frame_slider.setEnabled(False)
        self.frame_slider.valueChanged.connect(self.on_slider_changed)

    def init_layout(self, space_widget=None):
        self.layout_widget = QVBoxLayout(self)
        self.layout_widget.setContentsMargins(0, 0, 0, 0)

        value_layout = QHBoxLayout()
        value_layout.addWidget(self.min_index_label)
        value_layout.addWidget(self.current_index_label)
        value_layout.addWidget(self.max_index_label)

        self.layout_widget.addWidget(self.frame_label,1)
        if space_widget:
            self.layout_widget.addWidget(space_widget)
        self.layout_widget.addLayout(value_layout)
        self.layout_widget.addWidget(self.frame_slider)

    def update_viewer(self, index=0):
        try:
            is_empty = self.collection_v is None or len(self.collection_v.frames) == 0
            total_frame_index = 0 if is_empty else len(self.collection_v.frames)
            min_frame_index = 0 if is_empty else 1
            self.frame_slider.setRange(0, total_frame_index - 1)

            self.current_index_label.setText(f"{min_frame_index}" if not is_empty else "")
            self.min_index_label.setText(f"{min_frame_index}" if not is_empty else "")
            self.max_index_label.setText(f"{total_frame_index}" if not is_empty else "")

            if not is_empty and len(self.collection_v.frames) > index:
                if len(self.collection_v.frames) <= index: index = len(self.collection_v.frames) - 1
                if index < 0: index = 0
                self.show_frame(index)
                self.frame_slider.setValue(index)
                self.current_index_label.setEnabled(True)
                self.frame_slider.setEnabled(True)
            else:
                self.frame_label.setPixmap(QPixmap())
                self.current_index_label.setEnabled(False)
                self.frame_slider.setEnabled(False)
        except Exception as e:
            print(f"update_viewer Failed: {e}")

    def on_slider_changed(self, value):
        try:
            if self.collection_v is not None:
                if value < 0 or value >= len(self.collection_v.frames):
                    return
                self.current_index_label.setText(f"{value + 1}")
                self.show_frame(value)
        except Exception as e:
            print(f"Viewer Slider Change Failed: {e}")

    def on_slider_value_changed(self):
        try:
            value = self.frame_slider.value()
            if self.collection_v is not None:
                if value < 0 or value >= len(self.collection_v.frames):
                    return
                self.frame_slider.setValue(value)
                self.show_frame(value)
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

    def show_frame(self, frame_index):
        if self.collection_v is None or len(self.collection_v.frames) <= frame_index or frame_index < 0: return

        frame = self.collection_v.frames[frame_index]
        if isinstance(self.frame_label, CropLabel):
            self.frame_label.set_image(frame)
        else:
            UiUtils.show_frame(self.frame_label, frame)

    def reset(self):
        self.collection_v = None
        self.update_viewer()