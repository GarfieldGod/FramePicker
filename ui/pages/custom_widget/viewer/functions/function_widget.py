import enum

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton

from ui.pages.custom_widget.viewer.functions.crop_widget import CropLabel
from ui.pages.custom_widget.viewer.frame_viewer import FrameViewer

class FunctionType(enum.Enum):
    CROP = "Crop"
    CUT = "Cut"

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

        self.native_function = {
            FunctionType.CROP : (crop_setting.start_corp_func, crop_setting.apply_crop_func, crop_setting.cancel_crop_func),
            # FunctionType.CUT: (lambda :self.start_func(FunctionType.CUT), self.apply_crop_func, self.cancel_crop_func),
        }

        self.function_name = {
            FunctionType.CROP : (0, "Crop"),
            # FunctionType.CUT : (1, "Cut")
        }

        self.stack.addWidget(crop_setting)

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
            button.clicked.connect(lambda _, v=value: (self.frame_viewer.frame_label.set_ratio(v), print(v)))
            layout.addWidget(button)

    def start_corp_func(self):
        if not self.frame_viewer.collection_v: return
        self.frame_viewer.frame_label.start_cropping()
        self.frame_viewer.update_viewer(self.frame_viewer.frame_slider.value())

        self.function_widget.start_func(FunctionType.CROP)

    def apply_crop_func(self):
        if not self.frame_viewer.frame_label.is_cropping: return
        try:
            for index, frame in enumerate(self.frame_viewer.collection_v.frames):
                self.frame_viewer.collection_v.frames[index] = self.frame_viewer.frame_label.crop_image(frame)

            self.frame_viewer.update_collection_list()
            self.frame_viewer.update_viewer(self.frame_viewer.frame_slider.value())
            self.cancel_crop_func()
        except Exception as e:
            print(f"Apply functions func error: {e}")

    def cancel_crop_func(self):
        self.frame_viewer.frame_label.end_cropping()

        self.function_widget.cancel_func()

    def reset(self):
        self.cancel_crop_func()
