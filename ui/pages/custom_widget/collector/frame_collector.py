from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QListWidget, QPushButton, QVBoxLayout, QHBoxLayout, QListWidgetItem, \
    QLabel, QLineEdit, QDialog

from ui.collection_manager import Collection, CollectionManager, COLLECTIONS
from ui.pages.custom_widget.custom_thread import DownLoadThread
from ui.pages.custom_widget.custom_dialog import DownLoadFrameDialog, ProgressDialog, MessageBox
from ui.utils.ui_utils import UiUtils

class FrameCollector(QWidget):
    on_select_change = pyqtSignal(int)
    on_view_change = pyqtSignal(int, int)
    on_delete = pyqtSignal(int)

    def __init__(self):
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
        self.list_collections.setFocusPolicy(Qt.NoFocus)

    def init_ui_layout(self):
        layout_collector = QVBoxLayout(self)

        layout_buttons = QHBoxLayout()
        layout_buttons.addWidget(self.button_add_collection)
        layout_buttons.addWidget(self.button_delete_collection)

        layout_collector.addLayout(layout_buttons)
        layout_collector.addWidget(self.list_collections)

    def create_collection(self, collection):
        try:
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 100))

            widget_collection = CollectionWidget(collection)
            widget_collection.on_view.connect(
                lambda collection_id: self.view_collection(collection_id)
            )

            self.list_collections.addItem(item)
            self.list_collections.setItemWidget(item, widget_collection)

            if collection_type != "Empty":
                self.view_collection(widget_collection)
        except Exception as e:
            print(f"Create collection error: {e}")

    def delete_collection(self):
        selected_items = self.list_collections.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            widget = self.list_collections.itemWidget(item)
            # if widget is not None and len(widget.collection.frames) > 0:
            dlg = MessageBox("Are you sure you want to delete the collection?\n"
                             "\nThis collection is not empty!")
            if dlg.exec_() != QDialog.Accepted:
                return
            self.on_delete.emit(widget)
            self.list_collections.takeItem(self.list_collections.row(item))

    def select_collection(self, item):
        try:
            widget_collection = self.list_collections.itemWidget(item)
            if isinstance(widget_collection, Collection):
                self.reset_selected_collection(widget_collection)
                self.on_select_change.emit(widget_collection)
        except Exception as e:
            print(f"Select Change Failed: {e}")

    def view_collection(self, collection_id):
        try:
            if isinstance(collection, Collection):
                self.reset_view_collection(collection)
                self.on_view_change.emit(collection_id)
        except Exception as e:
            print(f"Select Change Failed: {e}")

    def reset_selected_collection(self, selected_widget=None):
        item_count = self.list_collections.count()
        for index in range(item_count):
            item = self.list_collections.item(index)
            widget = self.list_collections.itemWidget(item)
            if isinstance(widget, CollectionWidget):
                if selected_widget == widget:
                    widget.selected()
                else:
                    widget.not_selected()

    def reset_view_collection(self, selected_widget=None):
        item_count = self.list_collections.count()
        for index in range(item_count):
            item = self.list_collections.item(index)
            widget = self.list_collections.itemWidget(item)
            if isinstance(widget, CollectionWidget):
                if selected_widget == widget:
                    widget.viewing()
                else:
                    widget.not_viewing()

    def update_list(self):
        self.list_collections.clear()
        for collection in COLLECTIONS:
            self.create_collection(collection)


vStr="src"
sStr="dst"
vasStr="src&dst"
base_StyleSheet=(""
     "border-radius: 10px;"
     "font-weight: bold;"
     "color: white;")
vStr_StyleSheet=base_StyleSheet + "background-color: blue;"
sStr_StyleSheet=base_StyleSheet + "background-color: purple;"
vasStr_StyleSheet=base_StyleSheet + "background-color: red;"

class CollectionWidget(QWidget):
    on_view = pyqtSignal(int)

    frame_size = ""

    viewing_index = 0

    def __init__(self, collection):
        super(CollectionWidget, self).__init__()
        self.collection = collection

        self.frame_label = QLabel()
        self.collection_name_label = QLineEdit(f"{collection.collection_type} Collection")
        self.status_label = QLabel()
        self.total_frames_label = QLabel()
        self.frame_size_label = QLabel()

        self.view_collection_button =  QPushButton("Open in Viewer")
        self.download_button = QPushButton("DownLoad")

        self.init_func()
        self.init_ui()

    def init_func(self):
        self.update_collection_info()
        self.collection_name_label.setEnabled(True if self.collection.collection_type=="Empty" else False)

        self.frame_label.setStyleSheet("border: 1px solid #ccc;")
        self.frame_label.setAlignment(Qt.AlignCenter)
        self.frame_label.setFixedHeight(80)
        self.frame_label.setFixedWidth(80)

        self.status_label.setFixedWidth(80)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.view_collection_button.clicked.connect(lambda :self.on_view.emit(self.collection))
        self.download_button.clicked.connect(lambda :self.download_frames(self.collection.frames, self.collection_name_label.text()))

        if len(self.collection.frames) != 0:
            UiUtils.show_frame(self.frame_label, self.collection.frames[0])

    def init_ui(self):
        layout_collection_detail = QVBoxLayout()
        layout_collection_detail.addWidget(self.total_frames_label)
        layout_collection_detail.addWidget(self.frame_size_label)

        layout_buttons = QVBoxLayout()
        layout_buttons.setSpacing(0)
        layout_buttons.setContentsMargins(0,0,0,0)
        layout_buttons.addWidget(self.view_collection_button)
        layout_buttons.addWidget(self.download_button)

        layout_under_name = QHBoxLayout()
        layout_under_name.addLayout(layout_collection_detail)
        layout_under_name.addLayout(layout_buttons)

        layout_name_status = QHBoxLayout()
        layout_name_status.addWidget(self.collection_name_label,5)
        layout_name_status.addWidget(self.status_label)

        layout_part_2 = QVBoxLayout()
        layout_part_2.addLayout(layout_name_status)
        layout_part_2.addLayout(layout_under_name)

        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.frame_label)
        layout.addLayout(layout_part_2)

    def add_frame(self, frame):
        if len(self.collection.frames) == 0:
            UiUtils.show_frame(self.frame_label, frame)

        self.collection.frames.append(frame)
        self.update_collection_info()

    def delete_frame(self, index_to_delete):
        if index_to_delete < 0 or index_to_delete >= len(self.collection.frames): return
        del self.collection.frames[index_to_delete]

        self.update_collection_info()
        self.viewing_index = index_to_delete - 1 if index_to_delete - 1 >= 0 else 0
        self.on_view.emit(self.collection)

    def update_collection_info(self):
        total_frame = len(self.collection.frames)
        self.total_frames_label.setText(f"Total Frames: {total_frame}")
        self.frame_size_label.setText(f"Frames Size: {self.frame_size}")

        if total_frame == 0:
            self.frame_label.setPixmap(QPixmap())

    def download_frames(self, frames, collection_name):
        frame_count = len(frames)
        if not frames or frame_count == 0: return

        dlg = DownLoadFrameDialog(collection_name)
        if dlg.exec_() == QDialog.Accepted:
            file_path, file_name, file_format = dlg.values()
            if not file_path or not file_name or not file_name: return

            self.prg = ProgressDialog(
                f"DownLoad {collection_name}:",
                frame_count,
                operation="Download Frame")

            self.thread = DownLoadThread(
                frame_list=frames,
                output_dir=file_path,
                frame_prefix=file_name,
                frame_format=file_format
            )

            self.thread.download_one_finished.connect(
                self.prg.one_finished,
                Qt.QueuedConnection
            )
            self.thread.download_all_finished.connect(
                self.prg.all_finished,
                Qt.QueuedConnection
            )
            self.thread.start()
            self.prg.exec_()

    def viewing(self):
        current_text = self.status_label.text()
        if current_text == vStr or current_text == vasStr: return

        if current_text == sStr:
            self.status_label.setText(vasStr)
            self.status_label.setStyleSheet(vasStr_StyleSheet)
        else:
            self.status_label.setText(vStr)
            self.status_label.setStyleSheet(vStr_StyleSheet)

    def selected(self):
        current_text = self.status_label.text()
        if current_text == sStr or current_text == vasStr: return

        if current_text == vStr:
            self.status_label.setText(vasStr)
            self.status_label.setStyleSheet(vasStr_StyleSheet)
        else:
            self.status_label.setText(sStr)
            self.status_label.setStyleSheet(sStr_StyleSheet)

    def not_viewing(self):
        current_text = self.status_label.text()

        if current_text == vStr:
            self.status_label.clear()
            self.status_label.setStyleSheet("")
        if current_text == vasStr:
            self.status_label.setText(sStr)
            self.status_label.setStyleSheet(sStr_StyleSheet)

    def not_selected(self):
        current_text = self.status_label.text()

        if current_text == sStr:
            self.status_label.clear()
            self.status_label.setStyleSheet("")
        if current_text == vasStr:
            self.status_label.setText(vStr)
            self.status_label.setStyleSheet(vStr_StyleSheet)
