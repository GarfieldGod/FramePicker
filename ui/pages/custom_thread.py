from PyQt5.QtCore import QThread, pyqtSignal

from src.frame_picker import FramePicker


class DownLoadThread(QThread):
    download_one_finished = pyqtSignal(bool, str)
    download_all_finished = pyqtSignal(bool, str)

    def __init__(self, frame_list, output_dir, frame_prefix, frame_format):
        super().__init__()
        self.frame_list = frame_list
        self.output_dir = output_dir
        self.frame_prefix = frame_prefix
        self.frame_format = frame_format

    def run(self):
        all_success = True
        failed_index = []

        try:
            for index, frame in enumerate(self.frame_list):
                try:
                    success, ret = FramePicker.download_frame(
                        frame=frame,
                        output_dir=self.output_dir,
                        frame_prefix=self.frame_prefix,
                        frame_format=self.frame_format,
                        index=index
                    )
                except Exception as e:
                    success = False
                    ret = str(e)
                self.download_one_finished.emit(success, ret)
                if not success:
                    failed_index.append(index)
                    all_success = False

            if all_success:
                final_ret = "所有帧下载完成"
            else:
                final_ret = f"帧下载异常：{failed_index}"
        except Exception as e:
            all_success = False
            final_ret = f"线程执行异常：{e}"

        self.download_all_finished.emit(all_success, final_ret)

class DecodeThread(QThread):
    decode_one_finished = pyqtSignal(bool, str)
    decode_all_finished = pyqtSignal(bool, str)

    def __init__(self, frame_picker):
        super().__init__()
        self.frame_picker = frame_picker

    def run(self):
        failed_index = []

        try:
            all_success = self.frame_picker.decode(lambda success, ret: self.decode_one_finished.emit(success, f"Decode Frame Failed With Index {ret}"))
            if all_success:
                final_ret = "解码成功"
            else:
                final_ret = f"解码失败"
        except Exception as e:
            all_success = False
            final_ret = f"线程执行异常：{e}"

        self.decode_all_finished.emit(all_success, final_ret)