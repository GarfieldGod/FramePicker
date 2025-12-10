import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint


class CropLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.original_pixmap = None
        self.crop_rect = QRect(150, 100, 200, 150)
        self.drag_mode = None  # 'move', 'top', 'bottom', 'left', 'right', 'top_left', etc.
        self.mouse_pos = QPoint()
        self.min_size = 20  # 裁剪框最小宽高

        # 手柄区域大小（用于检测鼠标是否在边缘）
        self.handle_size = 8
        self.handle_color = QColor(255, 0, 0)  # 红色
        self.handle_hover_color = QColor(0, 255, 0)  # 悬停时绿色（可选）

    def set_image(self, cv_frame):
        if cv_frame is None:
            return
        height, width, channel = cv_frame.shape
        bytes_per_line = 3 * width
        q_img = QImage(cv_frame.data, width, height, bytes_per_line, QImage.Format_BGR888)
        self.original_pixmap = QPixmap.fromImage(q_img)
        self.setPixmap(self.original_pixmap)
        self.adjustSize()

    def get_handle_at_position(self, pos):
        """判断鼠标是否在某个手柄区域，返回操作类型"""
        rect = self.crop_rect
        x, y = pos.x(), pos.y()
        left, right = rect.left(), rect.right()
        top, bottom = rect.top(), rect.bottom()

        on_left = abs(x - left) <= self.handle_size
        on_right = abs(x - right) <= self.handle_size
        on_top = abs(y - top) <= self.handle_size
        on_bottom = abs(y - bottom) <= self.handle_size

        if on_left and on_top:
            return 'top_left'
        elif on_right and on_top:
            return 'top_right'
        elif on_left and on_bottom:
            return 'bottom_left'
        elif on_right and on_bottom:
            return 'bottom_right'
        elif on_left:
            return 'left'
        elif on_right:
            return 'right'
        elif on_top:
            return 'top'
        elif on_bottom:
            return 'bottom'
        elif rect.contains(pos):
            return 'move'
        else:
            return None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_mode = self.get_handle_at_position(event.pos())
            self.mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        if self.drag_mode is None:
            # 更新光标形状（可选）
            mode = self.get_handle_at_position(event.pos())
            cursor = Qt.ArrowCursor
            if mode in ('top', 'bottom'):
                cursor = Qt.SizeVerCursor
            elif mode in ('left', 'right'):
                cursor = Qt.SizeHorCursor
            elif mode in ('top_left', 'bottom_right'):
                cursor = Qt.SizeFDiagCursor
            elif mode in ('top_right', 'bottom_left'):
                cursor = Qt.SizeBDiagCursor
            elif mode == 'move':
                cursor = Qt.SizeAllCursor
            self.setCursor(cursor)
            return

        delta = event.pos() - self.mouse_pos
        rect = self.crop_rect
        new_rect = QRect(rect)

        # 根据 drag_mode 调整矩形
        if self.drag_mode == 'move':
            new_rect.translate(delta)
        elif self.drag_mode == 'top_left':
            new_rect.setTopLeft(new_rect.topLeft() + delta)
        elif self.drag_mode == 'top_right':
            new_rect.setTopRight(new_rect.topRight() + delta)
        elif self.drag_mode == 'bottom_left':
            new_rect.setBottomLeft(new_rect.bottomLeft() + delta)
        elif self.drag_mode == 'bottom_right':
            new_rect.setBottomRight(new_rect.bottomRight() + delta)
        elif self.drag_mode == 'top':
            new_rect.setTop(new_rect.top() + delta.y())
        elif self.drag_mode == 'bottom':
            new_rect.setBottom(new_rect.bottom() + delta.y())
        elif self.drag_mode == 'left':
            new_rect.setLeft(new_rect.left() + delta.x())
        elif self.drag_mode == 'right':
            new_rect.setRight(new_rect.right() + delta.x())

        # 限制在 QLabel 范围内
        new_rect.setLeft(max(0, new_rect.left()))
        new_rect.setTop(max(0, new_rect.top()))
        new_rect.setRight(min(self.width() - 1, new_rect.right()))
        new_rect.setBottom(min(self.height() - 1, new_rect.bottom()))

        # 保证最小尺寸
        if new_rect.width() < self.min_size:
            if self.drag_mode in ('left', 'top_left', 'bottom_left'):
                new_rect.setLeft(new_rect.right() - self.min_size)
            else:
                new_rect.setRight(new_rect.left() + self.min_size)
        if new_rect.height() < self.min_size:
            if self.drag_mode in ('top', 'top_left', 'top_right'):
                new_rect.setTop(new_rect.bottom() - self.min_size)
            else:
                new_rect.setBottom(new_rect.top() + self.min_size)

        self.crop_rect = new_rect
        self.mouse_pos = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_mode = None
            self.setCursor(Qt.ArrowCursor)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.original_pixmap:
            painter = QPainter(self)
            pen = QPen(self.handle_color, 2, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(self.crop_rect)

            # 可选：绘制手柄小方块（更直观）
            handle_pen = QPen(Qt.white, 1)
            painter.setPen(handle_pen)
            painter.setBrush(self.handle_color)
            handles = [
                self.crop_rect.topLeft(),
                self.crop_rect.topRight(),
                self.crop_rect.bottomLeft(),
                self.crop_rect.bottomRight(),
                QPoint(self.crop_rect.center().x(), self.crop_rect.top()),
                QPoint(self.crop_rect.center().x(), self.crop_rect.bottom()),
                QPoint(self.crop_rect.left(), self.crop_rect.center().y()),
                QPoint(self.crop_rect.right(), self.crop_rect.center().y()),
            ]
            for pt in handles:
                painter.drawRect(pt.x() - 3, pt.y() - 3, 6, 6)

    def crop_image(self, cv_frame):
        x = self.crop_rect.x()
        y = self.crop_rect.y()
        w = self.crop_rect.width()
        h = self.crop_rect.height()
        h_img, w_img = cv_frame.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = min(w, w_img - x)
        h = min(h, h_img - y)
        if w <= 0 or h <= 0:
            return np.array([])
        return cv_frame[y:y+h, x:x+w]

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("可调整裁剪框演示")
        self.resize(800, 600)

        # 使用摄像头或静态图
        self.cap = cv2.VideoCapture(0)
        ret, frame = self.cap.read()
        if not ret:
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        self.frame = frame
        self.label = CropLabel()
        self.label.set_image(frame)

        self.btn_crop = QPushButton("裁剪并保存")
        self.btn_crop.clicked.connect(self.save_cropped)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_crop)
        self.setLayout(layout)

    def save_cropped(self):
        cropped = self.label.crop_image(self.frame)
        if cropped.size > 0:
            cv2.imwrite("cropped_output.jpg", cropped)
            print("✅ 已保存裁剪图像到 cropped_output.jpg")
        else:
            print("❌ 裁剪区域无效")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())