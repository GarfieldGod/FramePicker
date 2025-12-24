import os.path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QVBoxLayout, QLineEdit, QComboBox, \
    QWidget, QLabel, QProgressBar, QScrollArea, QSpinBox, QSizePolicy, QStackedWidget

from src.collection.collection_manager import CollectionManager
from ui.pages.custom_widget.custom_widget import ResizingStackedWidget
from ui.template.ui_dialog import Dialog


class DownLoadFrameDialog(Dialog):
    download_format = ["png", "jpeg"]

    def __init__(self, collection_name, parent=None):
        self.file_path = QLineEdit(os.path.join(os.path.abspath("."), "output", collection_name))
        self.file_name = QLineEdit("default")
        self.file_format = QComboBox()
        self.file_format.addItems(self.download_format)

        super().__init__(title_text="DownLoad Frame:", parent=parent)


    def init_content_widget(self):
        layout_content = QVBoxLayout(self.content)

        layout_content.addWidget(QLabel("Output Path:"))
        layout_content.addWidget(self.file_path)
        layout_content.addWidget(QLabel("File Name:"))
        layout_content.addWidget(self.file_name)
        layout_content.addWidget(QLabel("File Format:"))
        layout_content.addWidget(self.file_format)

    def values(self):
        return self.file_path.text(), self.file_name.text(), self.file_format.currentText()

class ProgressDialog(Dialog):
    current_value = 0

    def __init__(self, title, total, operation="", auto_close=False, show_error=True, parent=None):
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)

        self.progress_label = QLabel(f"0/{total}")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_area = QScrollArea()
        self.error_area.setWidgetResizable(True)
        self.error_area.hide()
        self.error_widget = QWidget()
        self.error_layout = QVBoxLayout(self.error_widget)
        self.error_area.setWidget(self.error_widget)

        self.total_value = total
        self.operation = operation
        self.auto_close = auto_close
        self.show_error = show_error
        super().__init__(title_text=title, show_cancel_button=False, show_confirm_button=False, parent=parent)


    def init_content_widget(self):
        self.layout_content = QVBoxLayout(self.content)

        self.layout_content.addWidget(self.progress_label)
        self.layout_content.addWidget(self.progress_bar)
        self.layout_content.addWidget(self.error_area)

    def one_finished(self, success, ret):
        self.current_value += 1
        self.progress_bar.setValue(self.current_value)
        self.progress_label.setText(f"{self.operation}: {int(self.current_value/self.total_value * 100)}% ({self.current_value}/{self.total_value})")
        if not success:
            self.error_area.show()
            self.error_layout.addWidget(QLabel(f"{self.operation}: {self.current_value} Failed{f":\nError: {ret}" if self.show_error else ""}"))

    def all_finished(self, success, ret):
        self.current_value = 0
        ret_info = QLabel(f"{self.operation} {f"Failed:\nError: {ret}" if not success else "Success"}")
        ret_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout_content.addWidget(ret_info)
        if success and self.auto_close:
            self.close()
        self.show_confirm_button()

class MessageBox(Dialog):
    def __init__(self, message, message_name="Message:", parent=None):
        self.label_message = QLabel(message)

        super().__init__(title_text=message_name, title_height=30, button_right=False, parent=parent)

    def init_content_widget(self):
        self.label_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_message.setObjectName("MessageBox_Label")
        layout_content = QVBoxLayout(self.content)
        layout_content.setContentsMargins(30, 30, 30, 30)
        layout_content.setSpacing(0)

        layout_content.addWidget(self.label_message)

class NewCollectionDialog(Dialog):
    create_types = ["Empty", "Inheritance"]

    inherit_types = ["Specify Num"]

    string_desired_frame_count = "Desired Frame Count:"
    string_desired_interval = "Desired Interval:"

    def __init__(self, parent=None):
        try:
            self.collection_name = QLineEdit("New Collection")
            self.create_type = QComboBox()
            self.src_collection = QComboBox()
            self.inherit_type = QComboBox()
            int_validator = QIntValidator()
            self.inherit_input = QLineEdit()
            self.inherit_input.setValidator(int_validator)

            self.stack = ResizingStackedWidget()
            self.inherit_label = QLabel(self.string_desired_frame_count)

            super().__init__(title_text="Create Collection:", parent=parent)

            self.init_func()
        except Exception as e:
            print(f"Create collection ui failed: {e}")

    def init_func(self):
        self.create_type.addItems(self.create_types)
        self.create_type.setCurrentIndex(0)

        col_dict = CollectionManager.get_all_collections()

        for col_id in col_dict:
            col = col_dict[col_id]
            col_len = len(col.frames)
            if col_len <= 0:
                continue
            col_str = f"Name: [{col.collection_name}] Frame Count: [{str(col_len)}]"
            self.src_collection.addItem(col_str, col_id)

        self.src_collection_changed()

        self.inherit_type.addItems(self.inherit_types)
        self.inherit_type.setCurrentIndex(0)

        self.create_type.currentIndexChanged.connect(self.create_type_changed)
        self.src_collection.currentIndexChanged.connect(self.src_collection_changed)
        self.inherit_input.textChanged.connect(self.inherit_input_changed)

    def src_collection_changed(self):
        try:
            col_id = self.src_collection.currentData()
            col = CollectionManager.get_collection(col_id)
            if col is None: return
            col_len = len(col.frames)

            self.inherit_input.setText(str(int(col_len / 2)))
        except Exception as e:
            print(f"Source collection ui failed: {e}")

    def inherit_input_changed(self, value):
        try:
            if value == "" or int(value) < 1:
                self.inherit_input.setText(str(1))
                return
            col_id = self.src_collection.currentData()
            col = CollectionManager.get_collection(col_id)
            if col is None:
                return
            col_len = len(col.frames)
            if int(value) > col_len:
                self.inherit_input.setText(str(col_len))
        except Exception as e:
            print(f"Inherit input ui failed: {e}")

    def create_type_changed(self):
        self.stack.setCurrentIndex(self.create_type.currentIndex())

        self.adjustSize()

    def init_content_widget(self):
        layout_content = QVBoxLayout(self.content)

        layout_content.addWidget(QLabel("Collection Name:"))
        layout_content.addWidget(self.collection_name)
        layout_content.addWidget(QLabel("Create Type:"))
        layout_content.addWidget(self.create_type)

        layout_content.addWidget(self.stack)
        self.stack.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.stack.addWidget(QWidget())

        widget_inherit = QWidget()
        layout_inherit = QVBoxLayout(widget_inherit)
        widget_inherit.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        layout_inherit.addWidget(QLabel("Source Collection:"))
        layout_inherit.addWidget(self.src_collection)
        layout_inherit.addWidget(QLabel("Inherit Type:"))
        layout_inherit.addWidget(self.inherit_type)
        layout_inherit.addWidget(self.inherit_label)
        layout_inherit.addWidget(self.inherit_input)
        self.stack.addWidget(widget_inherit)

    def values(self):
        ret_dict = {
            "collection_name" : self.collection_name.text(),
            "create_type" : self.create_type.currentText(),
            "src_collection" : self.src_collection.currentData(),
            "inherit_type" : self.inherit_type.currentText(),
            "inherit_input": int(self.inherit_input.text()),
        }
        return ret_dict