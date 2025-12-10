from PyQt5.QtWidgets import QGroupBox, QHBoxLayout, QVBoxLayout

from ui.pages.custom_widget.crop_widget import CropLabel
from ui.pages.custom_widget.viewer.frame_viewer import FrameViewer
from ui.template.ui_page import PageContent, Container


class FrameCropPage(PageContent):
    # show_grid = True
    def __init__(self, y, x):
        

        super(FrameCropPage, self).__init__(y, x)

    def init_container(self):

        view = FrameCropContainer(3, 6)
        self.add_container(view, 0,0)

class FrameCropContainer(Container):
    def __init__(self, x, y):
        super(FrameCropContainer, self).__init__(x, y)
        self.crop_label = CropLabel()
        self.frame_viewer = FrameViewer( self.crop_label)
        
        # self.widget_frame_viewer.set_image(data_manager)

        self.init_ui_layout()

    def init_ui_layout(self):
        group_picker = QGroupBox(f"Viewer")
        layout_picker = QVBoxLayout(group_picker)

        layout_picker.addWidget(self.frame_viewer)

        layout_container = QHBoxLayout(self)
        layout_container.addWidget(group_picker)