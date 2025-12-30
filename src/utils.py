import cv2
import numpy as np

class Utils:
    @staticmethod
    def all_frames_in_one_picture(frame_list, cols):
        if len(frame_list) == 0:
            return None

        frame_height, frame_width, _ = frame_list[0].shape
        frames_bgra = []
        for frame in frame_list:
            frame_bgra = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
            frames_bgra.append(frame_bgra)

        rows = int(len(frame_list) / cols) + 1
        total_grid = rows * cols
        frame_count = len(frames_bgra)
        blank_count = total_grid - frame_count

        transparent_frames = []
        if blank_count > 0:
            blank_frame_bgra = np.zeros((frame_height, frame_width, 4), dtype=np.uint8)
            transparent_frames = [blank_frame_bgra for _ in range(blank_count)]

        all_frames = frames_bgra + transparent_frames

        grid_rows = []
        for i in range(rows):
            row_frames = all_frames[i * cols: (i + 1) * cols]
            row_img = cv2.hconcat(row_frames)
            grid_rows.append(row_img)

        final_grid_img = cv2.vconcat(grid_rows)

        return final_grid_img