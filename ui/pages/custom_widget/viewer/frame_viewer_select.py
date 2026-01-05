from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QHBoxLayout

from src.collection.collection import CollectionType
from src.collection.collection_manager import CollectionManager
from ui.pages.custom_widget.viewer.functions.function_widget import FunctionWidget
from ui.pages.custom_widget.viewer.frame_viewer import FrameViewer
from ui.template.widget.ui_custom_button import PushButton


class FrameViewerSelect(FrameViewer):
    collection_s = None
    update_collection = pyqtSignal(int, int)

    def __init__(self, frame_label=None, parent=None):
        self.button_add = PushButton("Add to Selected Collection")
        self.button_delete = PushButton("Delete from Viewing Collection")

        self.frame_label = frame_label
        self.function_widget = FunctionWidget(self)

        super(FrameViewerSelect, self).__init__(frame_label, parent)

        self.function_widget.init_func_widget()

        self.update_viewer()

    def init_ui(self):
        super(FrameViewerSelect, self).init_ui()

        self.button_add.clicked.connect(self.add_to_collection)
        self.button_delete.clicked.connect(self.delete_from_collection)

    def init_layout(self):
        super(FrameViewerSelect, self).init_layout(self.function_widget)

        collection_buttons_layout = QHBoxLayout()
        collection_buttons_layout.addWidget(self.button_add)
        collection_buttons_layout.addWidget(self.button_delete)

        self.layout_widget.addLayout(collection_buttons_layout)

    def update_viewer(self, index=0):
        super(FrameViewerSelect, self).update_viewer(index)

        self.update_add_delete_button()
        is_func_enabled = self.collection_v is not None and self.collection_v.collection_type != CollectionType.DECODE and len(self.collection_v.frames) != 0
        self.function_widget.set_function_enabled(True)

    def start_corp_func(self):
        if not self.collection_v: return

        if self.frame_label.is_cropping:
            self.frame_label.is_cropping = False
        else:
            self.frame_label.is_cropping = True

        self.update_viewer(self.frame_slider.value())

    def apply_crop_func(self):
        if not self.frame_label.is_cropping: return
        try:
            for index, frame in enumerate(self.collection_v.frames):
                self.collection_v.frames[index] = self.frame_label.crop_image(frame)

            self.update_collection_list()
            self.update_viewer(self.frame_slider.value())
        except Exception as e:
            print(e)

    def apply_resize_func(self):
        if not self.frame_label.is_resizing: return
        try:
            for index, frame in enumerate(self.collection_v.frames):
                self.collection_v.frames[index] = self.frame_label.resize_image(frame)

            self.update_collection_list()
            self.update_viewer(self.frame_slider.value())
        except Exception as e:
            print(e)

    def apply_flip_func(self):
        try:
            if self.frame_label.flip_type is None: return
            for index, frame in enumerate(self.collection_v.frames):
                self.collection_v.frames[index] = self.frame_label.flip_image(frame)

            self.frame_label.flip_type = None

            self.update_collection_list()
            self.update_viewer(self.frame_slider.value())
        except Exception as e:
            print(e)

    def apply_cut_func(self, start, end):
        try:
            self.collection_v.frames = self.collection_v.frames[start:end]
            self.update_collection_list()
            self.view_collection(self.collection_v.collection_id, 0)
        except Exception as e:
            print(e)

    def select_collection(self, collection_id):
        try:
            collection = CollectionManager.get_collection(collection_id)
            if collection is None: return

            self.collection_s = collection

            self.update_add_delete_button()
        except Exception as e:
            print(f"Viewer Select Collection Failed: {e}")

    def on_collection_deleted(self, collection_id):
        collection = CollectionManager.get_collection(collection_id)
        if collection is None: return
        if collection == self.collection_v:
            self.collection_v = None
            self.function_widget.reset()
        elif collection == self.collection_s:
            self.collection_s = None
        self.update_viewer()

    def get_add_delete_enabled(self):
        viewing_is_valid = (self.collection_v is not None) and (len(self.collection_v.frames) > 0)
        selected_is_valid = (self.collection_s is not None)
        viewing_is_selected = self.collection_s == self.collection_v
        add_button_enabled = (viewing_is_valid and selected_is_valid and not viewing_is_selected and
                              (self.collection_s.collection_type == CollectionType.CUSTOM))
        delete_button_enabled = (viewing_is_valid and selected_is_valid and viewing_is_selected and
                                 (self.collection_s.collection_type == CollectionType.CUSTOM))
        return add_button_enabled, delete_button_enabled

    def update_add_delete_button(self):
        try:
            add_button_enabled, delete_button_enabled = self.get_add_delete_enabled()
            self.button_add.setEnabled(add_button_enabled)
            self.button_delete.setEnabled(delete_button_enabled)
        except Exception as e:
            print(f"Viewer Update Button Failed: {e}")

    def add_to_collection(self):
        add_enabled, _ = self.get_add_delete_enabled()
        try:
            if add_enabled:
                frames = self.collection_v.frames
                frame_index = self.frame_slider.value()
                frame = frames[frame_index].copy()
                self.collection_s.add_frame(frame)
                self.update_collection_list()
        except Exception as e:
            print(f"Viewer Add Frame to Collection Failed: {e}")

    def delete_from_collection(self):
        if self.collection_v is None or self.collection_s is None: return
        _, delete_enabled = self.get_add_delete_enabled()
        try:
            if delete_enabled:
                frame_index = self.frame_slider.value()
                self.collection_s.delete_frame_by_index(frame_index)
                self.update_collection_list()
                self.update_viewer(frame_index - 1)
        except Exception as e:
            print(f"Viewer Delete Frame From Collection Failed: {e}")

    def update_collection_list(self):
        self.update_collection.emit(
            self.collection_v.collection_id if self.collection_v is not None else None,
            self.collection_s.collection_id if self.collection_s is not None else None
        )

    def view_collection(self, collection_id, viewing_index):
        super().view_collection(collection_id, viewing_index)

        self.function_widget.reset()
