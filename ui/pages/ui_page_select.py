from PyQt5.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout

from ui.pages.custom_widget.collector.frame_collector import FrameCollector
from ui.pages.custom_widget.viewer.functions.image_widget import CropLabel
from ui.pages.custom_widget.viewer.frame_viewer_select import FrameViewerSelect
from ui.template.ui_page import PageContent, Container

class FrameSelectorPage(PageContent):
    # show_grid = True
    def __init__(self, y, x):
        super(FrameSelectorPage, self).__init__(y, x)

    def init_container(self):

        view = FrameSelectorContainer(3, 6)
        self.add_container(view, 0,0)

        # view_dst = FrameSelectorContainer(3, 3)
        # self.add_container(view_dst, 3, 0)

        collector = FrameCollectorContainer(2,6)
        self.add_container(collector, 0,3)

        collector.list_collections.on_select_change.connect(
            view.widget_frame_viewer.select_collection
        )

        collector.list_collections.on_view_change.connect(
            view.widget_frame_viewer.view_collection
        )

        collector.list_collections.on_delete.connect(
            view.widget_frame_viewer.on_collection_deleted
        )

        view.widget_frame_viewer.update_collection.connect(
            collector.list_collections.update_list
        )

class FrameSelectorContainer(Container):
    def __init__(self, x, y):
        super(FrameSelectorContainer, self).__init__(x, y)
        self.crop_label = CropLabel()
        self.widget_frame_viewer = FrameViewerSelect(self.crop_label)

        self.init_ui_layout()

    def init_ui_layout(self):
        group_picker = QGroupBox(f"Viewer")
        layout_picker = QVBoxLayout(group_picker)

        layout_picker.addWidget(self.widget_frame_viewer)

        layout_container = QHBoxLayout(self)
        layout_container.addWidget(group_picker)

    def open_file(self, file_path):
        self.widget_frame_viewer.open_file(file_path)

class FrameCollectorContainer(Container):
    def __init__(self, x, y):
        super(FrameCollectorContainer, self).__init__(x, y)

        self.list_collections = FrameCollector()
        self.init_ui_layout()

    def init_ui_layout(self):
        group_collector = QGroupBox(f"Collections")
        layout_collector = QVBoxLayout(group_collector)

        layout_collector.addWidget(self.list_collections)

        layout_container = QHBoxLayout(self)
        layout_container.addWidget(group_collector)