import enum

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLineEdit

from ui.pages.custom_widget.viewer.functions.image_widget import CropLabel
from ui.pages.custom_widget.viewer.frame_viewer import FrameViewer

class FunctionType(enum.Enum):
    CROP = "Crop"
    RESIZE = "Resize"

class FunctionWidget(QWidget):
    def __init__(self, frame_viewer, height=80, parent=None):
        super(FunctionWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        self.function_widget = QWidget()
        self.setting_widget = QWidget()
        self.function_widget.setFixedHeight(height)
        self.setting_widget.setFixedHeight(height)
        self.setting_widget.hide()
        self.setting_layout = QHBoxLayout(self.setting_widget)
        self.function_layout = QHBoxLayout(self.function_widget)

        self.current_func = None
        self.stack = QStackedWidget(self)
        self.apply_func_button = QPushButton("√")
        self.cancel_func_button = QPushButton("×")

        self.init_layout()

        crop_setting = CropFunctionWidget(frame_viewer, self)
        resize_setting = ResizeFunctionWidget(frame_viewer, self)

        self.native_function = {
            FunctionType.CROP : self.get_function(crop_setting),
            FunctionType.RESIZE: self.get_function(resize_setting),
            # FunctionType.CUT: (self.start_func, self.apply_func, self.cancel_func),
        }

        self.function_name = {
            FunctionType.CROP : (0, "Crop"),
            FunctionType.RESIZE: (1, "Resize")
            # FunctionType.CUT : (1, "Cut")
        }

        self.stack.addWidget(crop_setting)
        self.stack.addWidget(resize_setting)

        self.init_func()

    def init_layout(self):
        self.layout.addWidget(self.setting_widget)
        self.layout.addWidget(self.function_widget)

        self.setting_layout.addStretch(2)
        self.setting_layout.addWidget(self.stack)
        self.setting_layout.addWidget(self.apply_func_button)
        self.setting_layout.addWidget(self.cancel_func_button)

        self.apply_func_button.setFixedSize(30, 30)
        self.cancel_func_button.setFixedSize(30, 30)
        self.apply_func_button.clicked.connect(lambda : self.run_function(1))
        self.cancel_func_button.clicked.connect(lambda : self.run_function(2))

    def get_function(self, widget):
        return widget.start_func, widget.apply_func, widget.cancel_func

    def run_function(self, index):
        if self.current_func is None: return
        self.native_function.get(self.current_func)[index]()

    def init_func(self):
        self.function_buttons = {}
        self.function_layout.addStretch()
        for key, value in self.native_function.items():
            function_button = QPushButton(str(self.function_name[key][1]))
            function_button.setFixedSize(50, 30)
            function_button.clicked.connect(value[0])
            self.function_layout.addWidget(function_button)
            self.function_buttons[key] = function_button
        self.function_layout.addStretch()

    def start_func(self, func_type):
        self.function_widget.hide()
        self.setting_widget.show()
        self.current_func = func_type
        self.stack.setCurrentIndex(self.function_name[func_type][0])

    def cancel_func(self):
        self.function_widget.show()
        self.setting_widget.hide()
        self.current_func = None

    def set_function_enabled(self, is_enabled, function_type=None):
        if function_type is None:
            for button in self.function_buttons.values():
                button.setEnabled(is_enabled)
        else:
            button = self.function_buttons.get(function_type)
            if button is not None:
                button.setEnabled(is_enabled)

    def reset(self):
        for index in range(self.stack.count()):
            widget = self.stack.widget(index)
            if widget is not None:
                widget.reset()

class CropFunctionWidget(QWidget):
    ratio_map = {
        "Free": None,
        "1:1": 1 / 1,
        "1:2": 1 / 2,
        "2:1": 2 / 1,
        "3:4": 3 / 4,
        "4:3": 4 / 3,
        "16:9": 16 / 9,
        "9:16": 9 / 16,
    }
    def __init__(self, frame_viewer, function_widget, parent=None):
        if not isinstance(frame_viewer, FrameViewer):
            raise TypeError('frame_viewer must be a FrameViewer')
        if not isinstance(frame_viewer.frame_label, CropLabel):
            raise TypeError('frame_label must be a CropLabel')
        super(CropFunctionWidget, self).__init__(parent)
        self.frame_viewer = frame_viewer
        self.function_widget = function_widget

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        for key, value in self.ratio_map.items():
            button = QPushButton(str(key))
            button.setFixedSize(50, 30)
            button.clicked.connect(lambda _, v=value: self.frame_viewer.frame_label.set_ratio(v))
            layout.addWidget(button)

    def start_func(self):
        if not self.frame_viewer.collection_v: return
        self.frame_viewer.frame_label.start_cropping()
        self.frame_viewer.update_viewer(self.frame_viewer.frame_slider.value())

        self.function_widget.start_func(FunctionType.CROP)

    def apply_func(self):
        if not self.frame_viewer.frame_label.is_cropping: return
        try:
            self.frame_viewer.apply_crop_func()
            self.cancel_func()
        except Exception as e:
            print(f"Apply functions func error: {e}")

    def cancel_func(self):
        self.frame_viewer.frame_label.end_cropping()

        self.function_widget.cancel_func()

    def reset(self):
        self.cancel_func()

class ResizeFunctionWidget(QWidget):
    def __init__(self, frame_viewer, function_widget, parent=None):
        if not isinstance(frame_viewer, FrameViewer):
            raise TypeError('frame_viewer must be a FrameViewer')
        if not isinstance(frame_viewer.frame_label, CropLabel):
            raise TypeError('frame_label must be a CropLabel')
        super(ResizeFunctionWidget, self).__init__(parent)
        self.frame_viewer = frame_viewer
        self.function_widget = function_widget

        self.height_input = QLineEdit()
        self.width_input = QLineEdit()

        self.origin_size = None

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        layout.addWidget(self.width_input)
        layout.addWidget(self.height_input)
        self.width_input.textEdited.connect(self.update_resize)
        self.height_input.textEdited.connect(self.update_resize)

    def start_func(self):
        try:
            if not self.frame_viewer.collection_v: return
            self.origin_size = self.frame_viewer.frame_label.get_original_size()
            self.width_input.setText(str(self.origin_size.width()))
            self.height_input.setText(str(self.origin_size.height()))
            self.frame_viewer.frame_label.start_resizing()

            self.function_widget.start_func(FunctionType.RESIZE)
        except Exception as e:
            print(f"start resize failed: {e}")

    def update_resize(self):
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())

            self.frame_viewer.frame_label.set_size(width, height)
            self.frame_viewer.update_viewer(self.frame_viewer.frame_slider.value())
        except Exception as e:
            print(f"update resize failed: {e}")

    def apply_func(self):
        try:
            if self.check_size():
                self.frame_viewer.apply_resize_func()
                self.origin_size = None
            self.cancel_func()
        except Exception as e:
            print(f"Apply functions func error: {e}")

    def cancel_func(self):
        try:
            if self.check_size():
                self.width_input.setText(str(self.origin_size.width()))
                self.height_input.setText(str(self.origin_size.height()))
                self.update_resize()

            self.origin_size = None
            self.frame_viewer.frame_label.end_resizing()
            self.function_widget.cancel_func()
        except Exception as e:
            print(f"Cancel resize failed: {e}")

    def check_size(self):
        if self.origin_size is not None:
            width = self.origin_size.width()
            height = self.origin_size.height()
            current_width = int(self.width_input.text())
            current_height = int(self.height_input.text())
            if current_width != width or current_height != height:
                return True
        return False

    def reset(self):
        self.cancel_func()