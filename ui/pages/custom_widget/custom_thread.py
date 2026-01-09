import time

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


class NanoPrecisionPlayThread(QThread):
    next_frame_index = pyqtSignal(int)
    play_finished = pyqtSignal()

    def __init__(self, total_frames: int = None, fps: int = None, parent=None):
        super().__init__(parent)
        self.total_frames = total_frames
        self.fps = fps

        self._is_playing = False
        self.is_loop = False
        self.start_index = 0
        self.current_index = 0
        self.start_nano = 0

    def start_play(self, total_frames, fps, start_index, is_loop):
        try:
            if self.total_frames == 0 or start_index >= total_frames:
                return

            self.total_frames = total_frames
            self.fps = fps

            self._is_playing = True
            self.is_loop = is_loop
            self.start_index = start_index
            self.current_index = start_index
            self.start_nano = time.perf_counter_ns()

            self.start()
            print(f"Play Thread Start")
        except Exception as e:
            print(f"NanoPrecisionPlayThread Start Play Failed: {e}")

    def stop_play(self):
        try:
            stop_index = self.current_index

            self._is_playing = False
            self.is_loop = False
            self.total_frames = None
            self.fps = None
            self.start_index = 0
            self.current_index = 0
            self.wait()
            print(f"Play Thread Stop")
            return stop_index
        except Exception as e:
            print(f"NanoPrecisionPlayThread Stop Play Failed: {e}")
            return -1

    def run(self):
        try:
            if not self.total_frames or not self.fps or self.fps == 0: return

            while self._is_playing and (self.is_loop or self.current_index < self.total_frames):
                target_nano = self.start_nano + (self.current_index - self.start_index) * (1_000_000_000 / self.fps)

                current_nano = time.perf_counter_ns()

                if current_nano < target_nano:
                    delta_nano = target_nano - current_nano
                    if delta_nano > 1_000_000:
                        time.sleep((delta_nano - 500_000) / 1_000_000_000)
                    while time.perf_counter_ns() < target_nano and self._is_playing:
                        pass

                if self._is_playing:
                    self.next_frame_index.emit(self.current_index % self.total_frames)
                    self.current_index += 1

            if self.current_index == self.total_frames:
                self.current_index = self.total_frames - 1

            if self._is_playing:
                self._is_playing = False
                self.play_finished.emit()
        except Exception as e:
            print(f"NanoPrecisionPlayThread Run Play Failed: {e}")