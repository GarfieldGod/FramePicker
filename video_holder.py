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

    def __init__(self, video_path):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"视频文件不存在：{video_path}")
        self.video_path = video_path
        self.open_video()

    def __del__(self):
        self.release()

    def open_video(self):
        self.video = cv2.VideoCapture(self.video_path)
        if not self.video.isOpened():
            raise RuntimeError(f"无法打开视频：{self.video_path}")

        self.init_video_info()
        self.init_frame_info()

    def init_video_info(self):
        self.fps = self.video.get(cv2.CAP_PROP_FPS)
        self.total_frame = int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        self.total_sec = self.total_frame / self.fps

    def init_frame_info(self):
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        ret, frame = self.video.read()
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.frame_origin_size = frame.shape[:2]

    def release(self):
        if self.video is not None:
            self.video.release()
            self.video = None

    def get_frames_by_interval(self,
        time_segment, frame_interval=1,
        output_dir="output", frame_prefix="video_clip", frame_format="png", time_line=False,
    ):
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"视频文件不存在：{self.video_path}")

        if frame_interval < 1:
            raise ValueError("帧间隔必须 ≥ 1")

        os.makedirs(output_dir, exist_ok=True)

        start_time, end_time = time_segment
        print(f"\n处理时间片段：{start_time} → {end_time}")
        start_sec = self.time_to_seconds(start_time)
        end_sec = self.time_to_seconds(end_time)

        if start_sec < 0 or end_sec <= start_sec or end_sec > self.total_sec:
            raise ValueError(f"警告：片段时间无效")

        start_frame = int(round(start_sec * self.fps))
        end_frame = int(round(end_sec * self.fps))

        frame_list = []
        for frame_idx in range(start_frame, end_frame + 1, frame_interval):
            frame_list.append(frame_idx)

        print(frame_list)

        self.get_frames(
            frame_list,
            output_dir, frame_prefix, frame_format)

    def get_frames_specify_num(self,
        time_segment, num_frames,
        output_dir="output", frame_prefix="video_clip", frame_format="png"
    ):
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"视频文件不存在：{self.video_path}")

        if num_frames < 1:
            raise ValueError("帧数量必须 ≥ 1")

        os.makedirs(output_dir, exist_ok=True)

        start_time, end_time = time_segment
        print(f"\n处理时间片段：{start_time} → {end_time}")
        start_sec = self.time_to_seconds(start_time)
        end_sec = self.time_to_seconds(end_time)

        if start_sec < 0 or end_sec <= start_sec or end_sec > self.total_sec:
            raise ValueError(f"警告：片段时间无效")

        start_frame = int(round(start_sec * self.fps))
        end_frame = int(round(end_sec * self.fps))

        if num_frames > end_frame - start_frame:
            raise ValueError("指定帧数量超过片段总帧数")

        self.video.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

        skip_frame_count = (end_frame - start_frame) // (num_frames - 1)
        frame_list = []
        current_frame = start_frame
        while current_frame <= end_frame:
            frame_list.append(current_frame)
            current_frame += skip_frame_count

        self.get_frames(
            frame_list,
            output_dir, frame_prefix, frame_format)

    def get_frames(self, frame_list, output_dir, frame_prefix, frame_format):
        current_frame = -1
        save_count = 0
        self.video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        for frame_index in range(self.total_frame):
            current_frame += 1
            if current_frame not in frame_list:
                self.video.read()
                continue

            ret, frame = self.video.read()
            if not ret:
                print(f"警告：读取帧 {current_frame} 失败，跳过")
                continue

            if self.resize_ is not None:
                frame = cv2.resize(frame, self.resize_, interpolation=cv2.INTER_AREA)

            if self.crop_ is not None:
                x1, y1, x2, y2 = self.crop_
                frame_height, frame_width = frame.shape[:2]
                x1 = max(0, min(x1, frame_width - 1))
                x2 = max(x1 + 1, min(x2, frame_width))
                y1 = max(0, min(y1, frame_height - 1))
                y2 = max(y1 + 1, min(y2, frame_height))

                frame = frame[y1:y2, x1:x2]
                print(
                    f"帧 {current_frame} 裁剪区域：({x1}, {y1}) → ({x2}, {y2})，裁剪后尺寸：{frame.shape[1]}×{frame.shape[0]}")

            frame_filename = f"{frame_prefix}_{save_count:04d}_{current_frame:04d}.{frame_format}"
            frame_path = os.path.join(output_dir, frame_filename)
            cv2.imwrite(frame_path, frame)

            save_count += 1
            print(f"已保存：{frame_path}（对应时间：{current_frame / self.fps:.2f} 秒）")

            if frame_list[len(frame_list) - 1] == current_frame:
                print("已保存所有帧数，跳过后续帧")
                break

        print(f"\n获取帧成功！总计保存 {save_count} 帧，路径：{output_dir}")

    def crop(self, crop_area=None):
        self.crop_ = crop_area

    def resize(self, size=None):
        self.resize_ = size

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

    time = ("00:00:00", "00:00:05")

    video_holder.resize((640, 480))
    video_holder.get_frames_by_interval(
        time_segment=time, frame_interval=20,
        output_dir="output/interval_clip", frame_prefix="interval_clip",
    )

    video_holder.resize()

    frame_shape = video_holder.frame_origin_size
    crop_region = get_center_crop_region(frame_shape, (800, 800))
    video_holder.crop(crop_region)

    video_holder.get_frames_specify_num(
        time_segment=time, num_frames=7,
        output_dir="output/specify_clip", frame_prefix="specify_clip",
    )