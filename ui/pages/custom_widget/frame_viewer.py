from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSlider, QPushButton, QLineEdit, QHBoxLayout

from ui.pages.custom_widget.frame_collector import Collection
from ui.utils.ui_utils import UiUtils


class FrameViewer(QWidget):
    frames = None
    selected_collection = None
    viewing_collection = None

    def __init__(self, data_manager, parent=None):
        super(FrameViewer, self).__init__(parent)

        self.frame_label = QLabel()

        self.button_add_to_collection = QPushButton("Add to Selected Collection")
        self.button_delete_from_collection = QPushButton("Delete from Viewing Collection")

        self.slider_value_max = QLabel()
        self.slider_value_min = QLabel()
        self.slider_value = QLineEdit()

        self.frame_slider = QSlider(Qt.Horizontal)

        self.init_ui()
        self.init_layout()

    def init_ui(self):
        self.frame_label.setStyleSheet("border: 1px solid #ccc;")
        self.frame_label.setAlignment(Qt.AlignCenter)

        self.button_add_to_collection.setEnabled(False)
        self.button_add_to_collection.clicked.connect(self.add_to_collection)
        self.button_delete_from_collection.setEnabled(False)
        self.button_delete_from_collection.clicked.connect(self.delete_from_collection)

        self.slider_value.setAlignment(Qt.AlignCenter)
        self.slider_value.setFixedWidth(100)
        self.slider_value_max.setAlignment(Qt.AlignRight)

        self.frame_slider.setSingleStep(1)
        self.frame_slider.valueChanged.connect(self.on_slider_changed)

    def init_layout(self):
        layout_widget = QVBoxLayout(self)
        layout_widget.setContentsMargins(0, 0, 0, 0)

        collection_buttons_layout = QHBoxLayout()
        collection_buttons_layout.addWidget(self.button_add_to_collection)
        collection_buttons_layout.addWidget(self.button_delete_from_collection)

        value_layout = QHBoxLayout()
        value_layout.addWidget(self.slider_value_min)
        value_layout.addWidget(self.slider_value)
        value_layout.addWidget(self.slider_value_max)

        layout_widget.addWidget(self.frame_label,1)
        layout_widget.addLayout(collection_buttons_layout)
        layout_widget.addLayout(value_layout)
        layout_widget.addWidget(self.frame_slider)

    def update_viewer(self):
        frames_empty = self.viewing_collection is None or len(self.viewing_collection.frames) == 0
        total_frame_index = 0 if frames_empty else len(self.viewing_collection.frames) - 1
        self.frame_slider.setRange(0, total_frame_index)
        self.frame_slider.setValue(0)

        self.slider_value.setText("0")
        self.slider_value_min.setText("0")
        self.slider_value_max.setText(f"{total_frame_index}")

        if not frames_empty:
            UiUtils.show_frame(self.frame_label, self.viewing_collection.frames[0])
        else:
            self.frame_label.setPixmap(QPixmap())

    def get_frame_data(self, frame_list):
        if not frame_list: return
        # self.frames = frame_list
        self.update_viewer()

    def on_slider_changed(self, value):
        try:
            if self.viewing_collection is not None:
                if value < 0 or value >= len(self.viewing_collection.frames):
                    return
                self.slider_value.setText(f"{value}")
                UiUtils.show_frame(self.frame_label, self.viewing_collection.frames[value])
                print(f"on_slider_changed {value}")
        except Exception as e:
            print(f"Viewer Slider Change Failed: {e}")

    def select_collection(self, widget_collection):
        try:
            if widget_collection is None or not isinstance(widget_collection, Collection): return

            self.selected_collection = widget_collection

            self.update_add_delete_button()
        except Exception as e:
            print(f"Viewer Select Collection Failed: {e}")

    def view_collection(self, widget_collection):
        try:
            if widget_collection is None or not isinstance(widget_collection, Collection): return
            # if (self.viewing_collection is not None and
            #     self.viewing_collection == widget_collection and
            #     len(self.viewing_collection.frames) == len(widget_collection.frames)): return
            # if len(widget_collection.frames) == 0: return

            self.viewing_collection = widget_collection
            self.get_frame_data(self.viewing_collection.frames)
            self.frame_slider.setValue(widget_collection.viewing_index)
            widget_collection.viewing_index = 0

            self.update_add_delete_button()
        except Exception as e:
            print(f"Viewer View Collection Failed: {e}")

    def get_add_delete_enabled(self):
        viewing_is_valid = (self.viewing_collection is not None) and (len(self.viewing_collection.frames) > 0)
        selected_is_valid = (self.selected_collection is not None)
        viewing_is_selected = self.selected_collection == self.viewing_collection
        add_button_enabled = (viewing_is_valid and selected_is_valid and not viewing_is_selected and
                              (self.selected_collection.collection_type == "Empty"))
        delete_button_enabled = (viewing_is_valid and selected_is_valid and viewing_is_selected and
                                 (self.selected_collection.collection_type == "Empty"))
        return add_button_enabled, delete_button_enabled

    def update_add_delete_button(self):
        try:
            add_button_enabled, delete_button_enabled = self.get_add_delete_enabled()
            self.button_add_to_collection.setEnabled(add_button_enabled)
            self.button_delete_from_collection.setEnabled(delete_button_enabled)
        except Exception as e:
            print(f"Viewer Update Button Failed: {e}")

    def add_to_collection(self):
        add_enabled, _ = self.get_add_delete_enabled()
        frames = self.viewing_collection.frames
        try:
            if add_enabled:
                frame_index = int(self.slider_value.text())
                frame = frames[frame_index].copy()
                self.selected_collection.add_frame(frame)
        except Exception as e:
            print(f"Viewer Add Frame to Collection Failed: {e}")

    def delete_from_collection(self):
        _, delete_enabled = self.get_add_delete_enabled()
        try:
            if delete_enabled:
                frame_index = int(self.slider_value.text())
                self.selected_collection.delete_frame(frame_index)
        except Exception as e:
            print(f"Viewer Delete Frame From Collection Failed: {e}")
