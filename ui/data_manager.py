
class DataManager:
    file_to_frame = {}
    def __init__(self):
        pass

    def add_file_frame(self, file_path, frame_data):
        self.file_to_frame[file_path] = frame_data