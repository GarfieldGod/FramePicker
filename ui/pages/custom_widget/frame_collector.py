from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QListWidgetItem, \
    QLabel, QLineEdit

from ui.utils.ui_utils import UiUtils

class FrameCollector(QWidget):
    on_select_change = pyqtSignal(QWidget)
    on_view_change = pyqtSignal(QWidget)

    def __init__(self, data_manager):
        super(FrameCollector, self).__init__()

        self.list_collections = QListWidget()
        self.button_add_collection = QPushButton("Add Collection")
        self.button_delete_collection = QPushButton("Delete Collection")

        self.init_ui_layout()
        self.init_functions()

    def init_functions(self):
        self.button_add_collection.clicked.connect(
            lambda _: self.create_collection([])
        )
        self.button_delete_collection.clicked.connect(self.delete_collection)

        self.list_collections.itemClicked.connect(self.select_collection)

    def init_ui_layout(self):
        layout_collector = QVBoxLayout(self)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_add_collection)
        layout_buttons.addWidget(self.button_delete_collection)

        layout_collector.addLayout(layout_buttons)
        layout_collector.addWidget(self.list_collections)

    def create_collection(self, frames_list, collection_type="Empty"):
        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 100))

        widget_collection = Collection(frames_list, collection_type)
        widget_collection.on_view.connect(
            lambda collection: self.on_view_change.emit(collection)
        )

        self.list_collections.addItem(item)
        self.list_collections.setItemWidget(item, widget_collection)

        if collection_type != "Empty":
            self.on_view_change.emit(widget_collection)

    def delete_collection(self):
        selected_items = self.list_collections.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.list_collections.takeItem(self.list_collections.row(item))

    def select_collection(self, item):
        try:
            widget_collection = self.list_collections.itemWidget(item)
            if isinstance(widget_collection, Collection):
                self.on_select_change.emit(widget_collection)
        except Exception as e:
            print(f"Select Change Failed: {e}")


class Collection(QWidget):
    on_view = pyqtSignal(QWidget)

    frame_size = ""
    collection_type = "Empty"
    frames = []

    viewing_index = 0

    def __init__(self, frames_list, collection_type="Empty"):
        super(Collection, self).__init__()
        self.frames = frames_list
        self.collection_type = collection_type

        self.frame_label = QLabel()
        self.collection_name_label = QLineEdit(f"{collection_type} Collection")
        self.total_frames_label = QLabel()
        self.frame_size_label = QLabel()

        self.view_collection_button =  QPushButton("Open in Viewer")

        self.init_func()
        self.init_ui()

    def init_func(self):
        self.update_collection_info()
        self.collection_name_label.setEnabled(True if self.collection_type=="Empty" else False)

        self.frame_label.setStyleSheet("border: 1px solid #ccc;")
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.frame_label.setFixedHeight(80)
        self.frame_label.setFixedWidth(80)

        self.view_collection_button.clicked.connect(self.view_collection)

        if len(self.frames) != 0:
            UiUtils.show_frame(self.frame_label, self.frames[0])

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft)

        layout_collection_info = QVBoxLayout()
        layout_collection_info.addWidget(self.collection_name_label)
        layout_collection_info.addWidget(self.total_frames_label)
        layout_collection_info.addWidget(self.frame_size_label)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.view_collection_button)

        layout.addWidget(self.frame_label)
        layout.addLayout(layout_collection_info)
        layout.addLayout(layout_buttons)

    def add_frame(self, frame):
        if len(self.frames) == 0:
            UiUtils.show_frame(self.frame_label, frame)

        self.frames.append(frame)
        self.update_collection_info()

    def delete_frame(self, index_to_delete):
        if index_to_delete < 0 or index_to_delete >= len(self.frames): return
        del self.frames[index_to_delete]

        self.update_collection_info()
        self.view_collection()
        self.viewing_index = index_to_delete - 1

    def update_collection_info(self):
        total_frame = len(self.frames)
        self.total_frames_label.setText(f"Total Frames: {total_frame}")
        self.frame_size_label.setText(f"Frames Size: {self.frame_size}")

        if total_frame == 0:
            self.frame_label.setPixmap(QPixmap())

    def view_collection(self):
        self.on_view.emit(self)