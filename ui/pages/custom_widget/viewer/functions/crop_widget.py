import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect, QPoint, QSize

from src.frame_picker import FramePicker


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
        self.handle_color = QColor(100, 255, 200)  # 红色
        self.handle_hover_color = QColor(0, 255, 0)  # 悬停时绿色（可选）
        self.is_cropping = False
        self.aspect_ratio = None

    def set_image(self, cv_frame):
        if cv_frame is None or cv_frame.size == 0:
            return

        orig_h, orig_w = cv_frame.shape[:2]

        if not cv_frame.flags['C_CONTIGUOUS']:
            cv_frame = np.ascontiguousarray(cv_frame)

        bytes_per_line = 3 * orig_w
        q_img = QImage(cv_frame.data, orig_w, orig_h, bytes_per_line, QImage.Format_BGR888)
        q_img = q_img.copy()

        scaled_pixmap = QPixmap.fromImage(q_img).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        # 计算实际显示区域（用于坐标映射）
        self.scaled_pixmap_size = scaled_pixmap.size()  # 如 QSize(800, 450)
        self.original_size = QSize(orig_w, orig_h)  # 如 QSize(1920, 1080)

        self.original_pixmap = scaled_pixmap
        self.setPixmap(scaled_pixmap)

        # 切换帧时调整裁剪框位置
        self._resize_crop_rect()

    def start_cropping(self):
        self.is_cropping = True
        self._init_crop_rect_to_center()

    def end_cropping(self):
        self.is_cropping = False
        self._init_crop_rect_to_center()

    def _resize_crop_rect(self):
        if self.original_pixmap and self.is_cropping:
            pixmap_offset_x, pixmap_offset_y = self._get_image_offset()

            self.crop_rect.moveTo(
                min(max(self.crop_rect.x(), pixmap_offset_x),
                    pixmap_offset_x + self.scaled_pixmap_size.width() - self.crop_rect.width()),
                min(max(self.crop_rect.y(), pixmap_offset_y),
                    pixmap_offset_y + self.scaled_pixmap_size.height() - self.crop_rect.height())
            )

    def _init_crop_rect_to_center(self):
        if not hasattr(self, 'scaled_pixmap_size'):
            return

        # 获取缩放后 pixmap 的尺寸和偏移（居中）
        pix_w = self.scaled_pixmap_size.width()
        pix_h = self.scaled_pixmap_size.height()
        offset_x, offset_y = self._get_image_offset()

        # 定义裁剪框大小
        crop_w = max(self.min_size, int(pix_w * 0.5))
        crop_h = max(self.min_size, int(pix_h * 0.5))

        if self.aspect_ratio:
            if self.aspect_ratio > 1:
                crop_h = max(self.min_size, round(crop_w / self.aspect_ratio))
            else:
                crop_w = max(self.min_size, round(crop_h * self.aspect_ratio))

        # 计算居中位置
        crop_x = offset_x + (pix_w - crop_w) // 2
        crop_y = offset_y + (pix_h - crop_h) // 2

        # 创建并设置裁剪框
        self.crop_rect = QRect(crop_x, crop_y, crop_w, crop_h)

    def _get_image_offset(self):
        if not hasattr(self, 'scaled_pixmap_size'):
            return 0, 0

        offset_x = (self.width() - self.scaled_pixmap_size.width()) // 2
        offset_y = (self.height() - self.scaled_pixmap_size.height()) // 2
        return offset_x, offset_y

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

        if on_left and on_top and not self.aspect_ratio:
            return 'top_left'
        elif on_right and on_top and not self.aspect_ratio:
            return 'top_right'
        elif on_left and on_bottom and not self.aspect_ratio:
            return 'bottom_left'
        elif on_right and on_bottom and not self.aspect_ratio:
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

    def _get_image_display_rect(self):
        if hasattr(self, 'scaled_pixmap_size'):
            pix_w = self.scaled_pixmap_size.width()
            pix_h = self.scaled_pixmap_size.height()
            offset_x = (self.width() - pix_w) // 2
            offset_y = (self.height() - pix_h) // 2
            return QRect(offset_x, offset_y, pix_w, pix_h)
        else:
            return self.rect()

    def mousePressEvent(self, event):
        if not self.is_cropping: return
        if event.button() == Qt.LeftButton:
            self.drag_mode = self.get_handle_at_position(event.pos())
            self.mouse_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if not self.is_cropping: return
        if event.button() == Qt.LeftButton:
            self.drag_mode = None
            self.setCursor(Qt.ArrowCursor)

    def free_crop_mode(self, old_rect, delta):
        # ========== 自由裁剪模式 ==========
        new_rect = QRect(old_rect)
        try:
            if self.drag_mode == 'move':
                new_rect.translate(delta)
            elif self.drag_mode == 'top_left':
                new_rect.setTopLeft(old_rect.topLeft() + delta)
            elif self.drag_mode == 'top_right':
                new_rect.setTopRight(old_rect.topRight() + delta)
            elif self.drag_mode == 'bottom_left':
                new_rect.setBottomLeft(old_rect.bottomLeft() + delta)
            elif self.drag_mode == 'bottom_right':
                new_rect.setBottomRight(old_rect.bottomRight() + delta)
            elif self.drag_mode == 'top':
                new_rect.setTop(old_rect.top() + delta.y())
            elif self.drag_mode == 'bottom':
                new_rect.setBottom(old_rect.bottom() + delta.y())
            elif self.drag_mode == 'left':
                new_rect.setLeft(old_rect.left() + delta.x())
            elif self.drag_mode == 'right':
                new_rect.setRight(old_rect.right() + delta.x())
        except Exception as e:
            print(f"free crop mode error: {e}")
        return new_rect

    def aspect_ratio_crop_mode(self, old_rect, delta):
        # ========== 比例裁剪模式 ==========
        new_rect = QRect(old_rect)
        try:
            if self.drag_mode == 'move':
                new_rect.translate(delta)
            elif self.drag_mode == 'top':
                new_rect.setTop(old_rect.top() + delta.y())
                width = new_rect.height() * self.aspect_ratio
                offset = round((width - new_rect.width()) / 2)
                new_rect.setLeft(old_rect.left() - offset)
                new_rect.setRight(old_rect.right() + offset)
            elif self.drag_mode == 'bottom':
                new_rect.setBottom(old_rect.bottom() + delta.y())
                width = new_rect.height() * self.aspect_ratio
                offset = round((width - new_rect.width()) / 2)
                new_rect.setLeft(old_rect.left() - offset)
                new_rect.setRight(old_rect.right() + offset)
            elif self.drag_mode == 'left':
                new_rect.setLeft(old_rect.left() + delta.x())
                height = new_rect.width() / self.aspect_ratio
                offset = round((height - new_rect.height()) / 2)
                new_rect.setTop(old_rect.top() - offset)
                new_rect.setBottom(old_rect.bottom() + offset)
            elif self.drag_mode == 'right':
                new_rect.setRight(old_rect.right() + delta.x())
                height = new_rect.width() / self.aspect_ratio
                offset = round((height - new_rect.height()) / 2)
                new_rect.setTop(old_rect.top() - offset)
                new_rect.setBottom(old_rect.bottom() + offset)
        except Exception as e:
            print(f"aspect ratio crop mode error: {e}")
        return new_rect

    def check_rect_scope(self, rect):
        img_rect = self._get_image_display_rect()
        if (rect.top() >= img_rect.top() and rect.bottom() <= img_rect.bottom()
            and rect.left() >= img_rect.left() and rect.right() <= img_rect.right()):
            if rect.width() >= self.min_size or rect.height() >= self.min_size:
                return True
        return False

    def mouseMoveEvent(self, event):
        try:
            if not self.is_cropping:
                return

            if self.drag_mode is None:
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
            old_rect = self.crop_rect

            if self.aspect_ratio is None:
                new_rect = self.free_crop_mode(old_rect, delta)
            else:
                new_rect = self.aspect_ratio_crop_mode(old_rect, delta)

            if self.check_rect_scope(new_rect):
                self.crop_rect = new_rect
            self.mouse_pos = event.pos()
            self.update()
        except Exception as e:
            print(f"mouseMoveEvent failed: {e}")

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.original_pixmap and self.is_cropping:
            painter = QPainter(self)
            pen = QPen(self.handle_color, 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self.crop_rect)

            # 绘制手柄小方块
            handle_pen = QPen(Qt.transparent, 1)
            painter.setPen(handle_pen)
            painter.setBrush(self.handle_hover_color)

            thickness = 2
            length = 12
            fixed_offset = 1
            draw_box = False

            if draw_box:
                handles = [
                    QPoint(self.crop_rect.topLeft()),
                    QPoint(self.crop_rect.topRight()),
                    QPoint(self.crop_rect.bottomLeft()),
                    QPoint(self.crop_rect.bottomRight()),
                    QPoint(self.crop_rect.center().x(), self.crop_rect.top()),
                    QPoint(self.crop_rect.center().x(), self.crop_rect.bottom()),
                    QPoint(self.crop_rect.left(), self.crop_rect.center().y()),
                    QPoint(self.crop_rect.right(), self.crop_rect.center().y()),
                ]
                for pt in handles:
                    painter.drawRect(pt.x() - thickness, pt.y() - thickness, thickness * 2, thickness * 2)
            else:
                # line
                painter.drawRect(self.crop_rect.center().x() - int(length / 2), self.crop_rect.top() - thickness, length, thickness * 2)
                painter.drawRect(self.crop_rect.center().x() - int(length / 2), self.crop_rect.bottom() - thickness + fixed_offset, length, thickness * 2)

                painter.drawRect(self.crop_rect.left() - thickness, self.crop_rect.center().y() - int(length / 2), thickness * 2, length)
                painter.drawRect(self.crop_rect.right() - thickness + fixed_offset, self.crop_rect.center().y() - int(length / 2), thickness * 2, length)

                # angle
                painter.drawRect(self.crop_rect.topLeft().x() - thickness, self.crop_rect.topLeft().y() - thickness, length + thickness, thickness * 2)
                painter.drawRect(self.crop_rect.topLeft().x() - thickness, self.crop_rect.topLeft().y() - thickness, thickness * 2, length + thickness)

                painter.drawRect(self.crop_rect.topRight().x() - length + fixed_offset, self.crop_rect.topRight().y() - thickness, length + thickness, thickness * 2)
                painter.drawRect(self.crop_rect.topRight().x() - thickness + fixed_offset, self.crop_rect.topRight().y() - thickness, thickness * 2, length + thickness)

                painter.drawRect(self.crop_rect.bottomLeft().x() - thickness, self.crop_rect.bottomLeft().y() - thickness + fixed_offset, length + thickness, thickness * 2)
                painter.drawRect(self.crop_rect.bottomLeft().x() - thickness, self.crop_rect.bottomLeft().y() - length + fixed_offset, thickness * 2, length + thickness)

                painter.drawRect(self.crop_rect.bottomRight().x() - length + fixed_offset, self.crop_rect.bottomRight().y() - thickness + fixed_offset,length + thickness, thickness * 2)
                painter.drawRect(self.crop_rect.bottomRight().x() - thickness + fixed_offset, self.crop_rect.bottomRight().y() - length + fixed_offset, thickness * 2, length + thickness)

    def map_label_to_original(self, rect_in_label: QRect) -> QRect:
        if not hasattr(self, 'scaled_pixmap_size') or not hasattr(self, 'original_size'):
            return QRect()

        # 获取 pixmap 在 QLabel 中的实际绘制位置（因为 KeepAspectRatio 会有居中偏移）
        pix_width = self.scaled_pixmap_size.width()
        pix_height = self.scaled_pixmap_size.height()

        # 计算 pixmap 左上角在 QLabel 中的偏移
        offset_x, offset_y = self._get_image_offset()

        # 裁剪框相对于 pixmap 的坐标（减去偏移）
        x_in_pixmap = rect_in_label.x() - offset_x
        y_in_pixmap = rect_in_label.y() - offset_y
        w_in_pixmap = rect_in_label.width()
        h_in_pixmap = rect_in_label.height()

        # 边界检查：确保在 pixmap 范围内
        x_in_pixmap = max(0, min(x_in_pixmap, pix_width - 1))
        y_in_pixmap = max(0, min(y_in_pixmap, pix_height - 1))
        w_in_pixmap = max(0, min(w_in_pixmap, pix_width - x_in_pixmap))
        h_in_pixmap = max(0, min(h_in_pixmap, pix_height - y_in_pixmap))

        if w_in_pixmap <= 0 or h_in_pixmap <= 0:
            return QRect()

        # 计算缩放比例
        scale_x = self.original_size.width() / pix_width
        scale_y = self.original_size.height() / pix_height

        # 映射回原始图像坐标
        x_orig = int(x_in_pixmap * scale_x)
        y_orig = int(y_in_pixmap * scale_y)
        w_orig = int(w_in_pixmap * scale_x)
        h_orig = int(h_in_pixmap * scale_y)

        return QRect(x_orig, y_orig, w_orig, h_orig)

    def crop_image(self, cv_frame):
        # 将 QLabel 上的 crop_rect 映射回原始图像坐标
        orig_rect = self.map_label_to_original(self.crop_rect)
        if orig_rect.isEmpty():
            return np.array([])

        x = orig_rect.x()
        y = orig_rect.y()
        w = orig_rect.width()
        h = orig_rect.height()

        h_img, w_img = cv_frame.shape[:2]
        x = max(0, min(x, w_img - 1))
        y = max(0, min(y, h_img - 1))
        w = min(w, w_img - x)
        h = min(h, h_img - y)

        if w <= 0 or h <= 0:
            return np.array([])

        return cv_frame[y:y + h, x:x + w]

    def set_ratio(self, ratio):
        try:
            if (not isinstance(self.aspect_ratio, float) and self.aspect_ratio is not None) or self.aspect_ratio == 0:
                raise Exception("Aspect ratio must be float and can't be zero")
            self.aspect_ratio = ratio
            self._init_crop_rect_to_center()
            self.update()
        except Exception as e:
            print(f"set ratio failed: {e}")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("可调整裁剪框演示")
        self.resize(800, 600)

        # 使用摄像头或静态图
        video_path = "../../../../../input/input.mp4"
        frame_picker = FramePicker(video_path)

        print(f"fps: {frame_picker.fps}")
        print(f"total_sec: {frame_picker.total_sec}")
        print(f"total_frame: {frame_picker.total_frame}")
        print(f"frame_origin_size: {frame_picker.frame_origin_size}")

        frame_picker.decode()
        frame = frame_picker.get_all_frames()[0]

        self.frame = frame
        self.label = CropLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 1px solid #ccc;")
        self.label.set_image(frame)
        self.label.is_cropping = True

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