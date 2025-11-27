import os
import cv2
from typing import Union, Tuple


class VideoHolder:
    video = None
    video_path = None
    fps = None
    total_sec = None
    total_frame = None
    resize_ = None
    crop_ = None
    frame_origin_size = None
    decoded_frames = None

    def __init__(self, video_path):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在：{video_path}")
        self.video_path = video_path
        self.open_video()

    def __del__(self):
        self.release()

    # public-----------------------------------------------------------
    def open_video(self):
        self.video = cv2.VideoCapture(self.video_path)
        if not self.video.isOpened():
            raise RuntimeError(f"无法打开视频：{self.video_path}")

        # init_video_info
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.total_frame = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.total_sec = self.total_frame / self.fps
        # init_frame_info
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.video.read()
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.frame_origin_size = frame.shape[:2]

    def release(self):
        if self.video is not None:
            self.video.release()
            self.video = None

    def decode(self):
        frames = {}
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for frame_index in range(self.total_frame):
            ret, frame = self.video.read()
            if not ret:
                print(f"警告：解码帧 {frame_index} 失败，跳过")
                continue
            frames[frame_index] = frame
        self.decoded_frames = frames

    def get_frames_index_by_interval(self, time_segment, frame_interval=1):
        if frame_interval < 1:
            raise ValueError("帧间隔必须 ≥ 1")

        start_frame, end_frame = self.get_start_end_frame_index(time_segment)

        frame_index_list = []
        for frame_idx in range(start_frame, end_frame + 1, frame_interval):
            frame_index_list.append(frame_idx)

        return frame_index_list

    def get_frames_index_by_specify_num(self, time_segment, num_frames):
        if num_frames < 1:
            raise ValueError("帧数量必须 ≥ 1")

        start_frame, end_frame = self.get_start_end_frame_index(time_segment)

        if num_frames > end_frame - start_frame:
            raise ValueError("指定帧数量超过片段总帧数")

        skip_frame_count = (end_frame - start_frame) // (num_frames - 1)

        frame_index_list = []
        current_frame = start_frame
        while current_frame <= end_frame:
            frame_index_list.append(current_frame)
            current_frame += skip_frame_count

        return frame_index_list

    def crop(self, crop_area=None):
        self.crop_ = crop_area

    def resize(self, size=None):
        self.resize_ = size

    def download_frames(self, frame_index_list, output_dir, frame_prefix, frame_format):
        os.makedirs(output_dir, exist_ok=True)
        save_count = 0
        for frame_index in frame_index_list:
            if frame_index not in self.decoded_frames:
                print(f"警告：读取帧 {frame_index} 失败，跳过")
                continue

            frame = self.decoded_frames[frame_index]
            frame = self.apply_resize(frame)
            frame = self.apply_crop(frame)

            frame_filename = f"{frame_prefix}_{save_count:04d}_{frame_index:04d}.{frame_format}"
            frame_path = os.path.join(output_dir, frame_filename)
            cv2.imwrite(frame_path, frame)

            save_count += 1
            print(f"下载：{frame_path}（对应时间：{frame_index / self.fps:.2f} 秒）")

        print(f"\n下载帧成功！总计保存 {save_count} 帧，路径：{output_dir}")

    # private-----------------------------------------------------------
    def get_start_end_frame_index(self, time_segment):
        start_time, end_time = time_segment
        start_sec = self.time_to_seconds(start_time)
        end_sec = self.time_to_seconds(end_time)

        if start_sec < 0 or end_sec <= start_sec or end_sec > self.total_sec:
            raise ValueError(f"警告：片段时间无效")

        start_frame = int(round(start_sec * self.fps))
        end_frame = int(round(end_sec * self.fps))
        return start_frame, end_frame

    def apply_resize(self, frame):
        if self.resize_ is not None:
            frame = cv2.resize(frame, self.resize_, interpolation=cv2.INTER_AREA)

        return frame

    def apply_crop(self, frame):
        if self.crop_ is not None:
            x1, y1, x2, y2 = self.crop_
            frame_height, frame_width = frame.shape[:2]
            x1 = max(0, min(x1, frame_width - 1))
            x2 = max(x1 + 1, min(x2, frame_width))
            y1 = max(0, min(y1, frame_height - 1))
            y2 = max(y1 + 1, min(y2, frame_height))

            frame = frame[y1:y2, x1:x2]

        return frame

    @staticmethod
    def time_to_seconds(time_val: Union[float, str]) -> float:
        if isinstance(time_val, float):
            return time_val
        elif isinstance(time_val, str):
            parts = list(map(int, time_val.split(":")))
            if len(parts) == 3:
                return parts[0] * 3600 + parts[1] * 60 + parts[2]
            elif len(parts) == 2:
                return parts[0] * 60 + parts[1]
            elif len(parts) == 1:
                return parts[0]
            else:
                raise ValueError(f"无效时间格式：{time_val}")
        else:
            raise TypeError(f"时间类型错误：{type(time_val)}")

def get_center_crop_region(frame_shape: Tuple[int, int], crop_size: Tuple[int, int]) -> Tuple[int, int, int, int]:
    frame_h, frame_w = frame_shape
    crop_w, crop_h = crop_size

    # 计算居中坐标
    x1 = (frame_w - crop_w) // 2
    y1 = (frame_h - crop_h) // 2
    x2 = x1 + crop_w
    y2 = y1 + crop_h

    return (x1, y1, x2, y2)

if __name__ == "__main__":

    video_path = "input/input.mp4"
    video_holder = VideoHolder(video_path)

    print(f"fps: {video_holder.fps}")
    print(f"total_sec: {video_holder.total_sec}")
    print(f"total_frame: {video_holder.total_frame}")
    print(f"frame_origin_size: {video_holder.frame_origin_size}")

    video_holder.decode()

    time = ("00:00:00", "00:00:05")

    video_holder.resize((640, 480))
    index_list = video_holder.get_frames_index_by_interval(time_segment=time, frame_interval=20)
    video_holder.download_frames(frame_index_list=index_list, output_dir="output/interval_clip", frame_prefix="interval_clip",frame_format="png")

    video_holder.resize()

    frame_shape = video_holder.frame_origin_size
    crop_region = get_center_crop_region(frame_shape, (800, 800))
    video_holder.crop(crop_region)

    index_list = video_holder.get_frames_index_by_specify_num(time_segment=time, num_frames=7)
    video_holder.download_frames(frame_index_list=index_list, output_dir = "output/specify_clip", frame_prefix = "specify_clip",frame_format="png")