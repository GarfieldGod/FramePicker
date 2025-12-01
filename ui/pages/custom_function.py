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
        final_ret = "所有帧下载完成"

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
                    print(e)
                    success = False
                    ret = str(e)
                self.download_one_finished.emit(success, ret)
                if not success:
                    all_success = False
                    final_ret = f"第{index}帧下载失败：{ret}"
        except Exception as e:
            all_success = False
            final_ret = f"下载异常：{str(e)}"
            print(f"线程执行异常：{e}")

        self.download_all_finished.emit(all_success, final_ret)