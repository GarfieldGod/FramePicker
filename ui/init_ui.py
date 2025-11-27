import sys

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QApplication

from ui.pages.ui_page_task import FrameSelectorPage
from ui.template.ui_main_window import MainWindow
from ui.template.ui_page import PageNavigation

def init_page_list(w):
    nav_frame_selector = PageNavigation(name="Select")
    con_frame_selector = FrameSelectorPage(6,6)
    w.add_page(nav_frame_selector, con_frame_selector)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(
        title_text="Frame Picker",
        title_desc="--Pick Your Frames from AI-Generated Videos",
        window_size=QSize(1920, 1080)
    )
    init_page_list(window)
    window.show()
    sys.exit(app.exec_())