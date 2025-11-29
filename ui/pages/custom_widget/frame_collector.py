import cv2
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QWidget, QListWidget, QPushButton, QGroupBox, QVBoxLayout, QHBoxLayout, QListWidgetItem, \
    QLabel, QLineEdit

from ui.utils.ui_utils import UiUtils

class FrameCollector(QWidget):
    collections = []
    def __init__(self, data_manager):
        super(FrameCollector, self).__init__()

        self.list_collections = QListWidget()
        self.button_add_collection = QPushButton("Add Collection")
        self.button_delete_collection = QPushButton("Delete Collection")

        self.init_ui_layout()
        self.init_functions()

    def init_functions(self):
        self.button_add_collection.clicked.connect(self.create_collection)
        self.button_delete_collection.clicked.connect(self.delete_collection)

    def init_ui_layout(self):
        layout_collector = QVBoxLayout(self)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_add_collection)
        layout_buttons.addWidget(self.button_delete_collection)

        layout_collector.addLayout(layout_buttons)
        layout_collector.addWidget(self.list_collections)

    def create_collection(self):
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 100))

        widget_collection = Collection()

        self.list_collections.addItem(item)
        self.list_collections.setItemWidget(item, widget_collection)

    def delete_collection(self):
        selected_items = self.list_collections.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.list_collections.takeItem(self.list_collections.row(item))

class Collection(QWidget):
    frame_size = ""
    frames = set()
    is_empty = True

    def __init__(self):
        super(Collection, self).__init__()
        self.frame_label = QLabel()
        self.collection_name_label = QLineEdit("Empty Collection")
        self.total_frames_label = QLabel("Total Frames: 0")
        self.frame_size_label = QLabel("Frames Size: 0 x 0")

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft)

        self.frame_label.setStyleSheet("border: 1px solid #ccc;")
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.frame_label.setFixedWidth(80)

        layout_collection_info = QVBoxLayout()
        layout_collection_info.addWidget(self.collection_name_label)
        layout_collection_info.addWidget(self.total_frames_label)
        layout_collection_info.addWidget(self.frame_size_label)

        layout.addWidget(self.frame_label)
        layout.addLayout(layout_collection_info)

    def add_frame(self, frame_index):
        self.frames.add(frame_index)

        if self.is_empty:
            self.is_empty = False
            UiUtils.show_frame(self.frame_label, frame)

        self.total_frames_label = QLabel(f"Total Frames: {len(self.frames)}")
        self.frame_size_label = QLabel(f"Frames Size: {self.frame_size}")