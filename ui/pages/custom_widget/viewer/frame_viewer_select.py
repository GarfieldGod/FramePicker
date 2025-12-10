from PyQt5.QtWidgets import QPushButton, QHBoxLayout

from ui.collection_manager import CollectionManager
from ui.pages.custom_widget.viewer.frame_viewer import FrameViewer


class FrameViewerSelect(FrameViewer):
    collection_s = None

    def __init__(self, frame_label=None, parent=None):
        self.button_add = QPushButton("Add to Selected Collection")
        self.button_delete = QPushButton("Delete from Viewing Collection")

        super(FrameViewerSelect, self).__init__(frame_label, parent)

    def init_ui(self):
        super(FrameViewerSelect, self).init_ui()

        self.button_add.setEnabled(False)
        self.button_add.clicked.connect(self.add_to_collection)
        self.button_delete.setEnabled(False)
        self.button_delete.clicked.connect(self.delete_from_collection)

    def init_layout(self):
        super(FrameViewerSelect, self).init_layout()

        collection_buttons_layout = QHBoxLayout()
        collection_buttons_layout.addWidget(self.button_add)
        collection_buttons_layout.addWidget(self.button_delete)

        self.layout_widget.addLayout(collection_buttons_layout)

    def update_viewer(self, index=0):
        super(FrameViewerSelect, self).update_viewer(index)

        self.update_add_delete_button()

    def select_collection(self, collection_id):
        try:
            collection = CollectionManager.get_collection(collection_id)
            if collection is None: return

            self.collection_s = collection

            self.update_add_delete_button()
        except Exception as e:
            print(f"Viewer Select Collection Failed: {e}")

    def delete_collection(self, collection_id):
        collection = CollectionManager.get_collection(collection_id)
        if collection is None: return
        if collection == self.collection_v:
            self.collection_v = None
        elif collection == self.collection_s:
            self.collection_s = None
        self.update_viewer()

    def get_add_delete_enabled(self):
        viewing_is_valid = (self.collection_v is not None) and (len(self.collection_v.frames) > 0)
        selected_is_valid = (self.collection_s is not None)
        viewing_is_selected = self.collection_s == self.collection_v
        add_button_enabled = (viewing_is_valid and selected_is_valid and not viewing_is_selected and
                              (self.collection_s.collection_type == "Empty"))
        delete_button_enabled = (viewing_is_valid and selected_is_valid and viewing_is_selected and
                                 (self.collection_s.collection_type == "Empty"))
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
        frames = self.collection_v.frames
        try:
            if add_enabled:
                frame_index = int(self.slider_value.text()) - 1
                frame = frames[frame_index].copy()
                self.collection_s.add_frame(frame)
        except Exception as e:
            print(f"Viewer Add Frame to Collection Failed: {e}")

    def delete_from_collection(self):
        _, delete_enabled = self.get_add_delete_enabled()
        try:
            if delete_enabled:
                frame_index = int(self.slider_value.text()) - 1
                self.collection_s.delete_frame(frame_index)
        except Exception as e:
            print(f"Viewer Delete Frame From Collection Failed: {e}")
