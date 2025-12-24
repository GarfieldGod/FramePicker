import enum

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QPushButton, QLineEdit, QLabel

from ui.pages.custom_widget.viewer.functions.image_widget import CropLabel
from ui.pages.custom_widget.viewer.frame_viewer import FrameViewer

class FunctionType(enum.Enum):
    PLAY = "Play"
    CROP = "Crop"
    RESIZE = "Resize"

class FunctionWidget(QWidget):
    def __init__(self, frame_viewer, height=70, parent=None):
        super(FunctionWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.frame_viewer = frame_viewer

        self.function_widget = QWidget()
        self.setting_widget = QWidget()
        self.function_widget.setFixedHeight(height)
        self.setting_widget.setFixedHeight(height)
        self.setting_widget.hide()
        self.setting_layout = QHBoxLayout(self.setting_widget)
        self.function_layout = QHBoxLayout(self.function_widget)
        # self.setting_layout.setSpacing(0)
        self.setting_layout.setContentsMargins(0, 0, 0, 0)
        self.function_layout.setSpacing(15)
        self.function_layout.setContentsMargins(0, 0, 0, 0)

        self.current_func = None
        self.stack = QStackedWidget(self)
        self.apply_func_button = QPushButton("√")
        self.cancel_func_button = QPushButton("×")

        self.init_layout()

    def init_func_widget(self):
        play_setting = PlayFunctionWidget(self.frame_viewer, self)
        crop_setting = CropFunctionWidget(self.frame_viewer, self)
        resize_setting = ResizeFunctionWidget(self.frame_viewer, self)

        self.native_function = {
            FunctionType.PLAY: self.get_function(play_setting),
            FunctionType.CROP: self.get_function(crop_setting),
            FunctionType.RESIZE: self.get_function(resize_setting),
            # FunctionType.CUT: (self.start_func, self.apply_func, self.cancel_func),
        }

        self.function_name = {
            FunctionType.PLAY: (0, "Play"),
            FunctionType.CROP: (1, "Crop"),
            FunctionType.RESIZE: (2, "Resize")
            # FunctionType.CUT : (1, "Cut")
        }

        self.stack.addWidget(play_setting)
        self.stack.addWidget(crop_setting)
        self.stack.addWidget(resize_setting)

        self.init_func()

    def init_layout(self):
        self.layout.addWidget(self.setting_widget)
        self.layout.addWidget(self.function_widget)

        self.setting_layout.addStretch(2)
        self.setting_layout.addWidget(self.stack)
        self.setting_layout.addStretch(1)
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

    def start_func(self, func_type, show_apply=True, show_cancel=True):
        self.function_widget.hide()
        self.setting_widget.show()

        if not show_apply:
            self.apply_func_button.hide()
        else:
            self.apply_func_button.show()

        if not show_cancel:
            self.cancel_func_button.hide()
        else:
            self.cancel_func_button.show()

        self.current_func = func_type
        self.stack.setCurrentIndex(self.function_name[func_type][0])

    def cancel_func(self):
        self.function_widget.show()
        self.setting_widget.hide()
        self.apply_func_button.show()
        self.cancel_func_button.show()
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
        self.height_input.setFixedWidth(100)
        self.width_input.setFixedWidth(100)
        int_validator = QIntValidator()
        self.height_input.setValidator(int_validator)
        self.width_input.setValidator(int_validator)

        self.origin_size = None

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.addStretch()
        layout.addWidget(QLabel("Width:"))
        layout.addWidget(self.width_input)
        layout.addWidget(QLabel("Height:"))
        layout.addWidget(self.height_input)
        layout.addStretch()
        self.width_input.textEdited.connect(self.update_resize)
        self.height_input.textEdited.connect(self.update_resize)
        self.width_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.height_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

class PlayFunctionWidget(QWidget):
    def __init__(self, frame_viewer, function_widget, parent=None):
        if not isinstance(frame_viewer, FrameViewer):
            raise TypeError('frame_viewer must be a FrameViewer')
        if not isinstance(frame_viewer.frame_label, CropLabel):
            raise TypeError('frame_label must be a CropLabel')
        super(PlayFunctionWidget, self).__init__(parent)
        self.frame_viewer = frame_viewer
        self.function_widget = function_widget

        self.fps_input = QLineEdit()
        self.play_button = QPushButton("Play")
        self.play_from_start_button = QPushButton("Play from Start")

        self.is_playing = False

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        layout.addStretch(1)
        layout.addWidget(QLabel("FPS:"))
        layout.addWidget(self.fps_input)
        layout.addWidget(self.play_button)
        layout.addWidget(self.play_from_start_button)
        layout.addStretch(1)

        self.play_button.clicked.connect(lambda : self.play_collection(-1))
        self.play_from_start_button.clicked.connect(lambda : self.play_collection(0))
        self.frame_viewer.nano_play_thread.play_finished.connect(self.finished_play)

        int_validator = QIntValidator()
        self.fps_input.setValidator(int_validator)
        self.fps_input.setFixedWidth(100)
        self.fps_input.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def start_func(self):
        try:
            if not self.frame_viewer.collection_v: return
            fps = self.frame_viewer.collection_v.fps
            if not fps: fps = 8
            self.fps_input.setText(str(fps))
            self.function_widget.start_func(FunctionType.PLAY, show_apply=False)
        except Exception as e:
            print(f"Start play failed: {e}")

    def apply_func(self):
        try:
            pass
        except Exception as e:
            print(f"Apply functions func error: {e}")

    def cancel_func(self):
        try:
            self.frame_viewer.stop_playing()
            self.finished_play()

            self.function_widget.cancel_func()
        except Exception as e:
            print(f"Cancel play failed: {e}")

    def reset(self):
        self.cancel_func()

    def play_collection(self, start_index):
        try:
            if self.is_playing:
                self.frame_viewer.stop_playing()
                self.finished_play()
            else:
                fps = float(self.fps_input.text())
                if self.frame_viewer.play_collection(fps, start_index):
                    self.fps_input.setEnabled(False)
                    self.play_button.setText("Stop")
                    self.is_playing = True
        except Exception as e:
            print(f"Function Widget Play Collection Failed: {e}")

    def finished_play(self):
        self.play_button.setText("Play")
        self.is_playing = False
        self.fps_input.setEnabled(True)