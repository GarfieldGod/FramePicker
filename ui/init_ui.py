import os
import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication

from ui.pages.ui_page_crop import FrameCropPage
from ui.pages.ui_page_select import FrameSelectorPage
from ui.template.ui_custom_function import get_ui_resource_path
from ui.template.ui_main_window import MainWindow
from ui.template.ui_page import PageNavigation

def init_page_list(w):
    nav_frame_selector = PageNavigation(name="Select")
    con_frame_selector = FrameSelectorPage(6,5)
    w.add_page(nav_frame_selector, con_frame_selector)

    nav_frame_crop = PageNavigation(name="Crop")
    con_frame_crop = FrameCropPage(6,5)
    w.add_page(nav_frame_crop, con_frame_crop)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    window = MainWindow(
        title_text="Frame Picker",
        title_desc="--Pick Your Frames from AI-Generated Videos",
        window_size=QSize(1440, 900),
        icon_path=os.path.join(get_ui_resource_path(), "image", "frame_picker_right.png"),
        window_icon=os.path.join(get_ui_resource_path(), "image", "frame_picker_enhanced.png"),
        icon_size=QSize(90, 120),
    )
    init_page_list(window)
    window.show()
    sys.exit(app.exec_())