from enum import Enum

class CollectionType(Enum):
    DECODE = "Decode"
    CUSTOM = "Custom"

class Collection:
    def __init__(self, collection_name: str, frames_list: list,
                 collection_type: CollectionType, collection_id: int,
                 collection_fps: int):
        self.collection_name = collection_name
        self.collection_type = collection_type
        self.collection_id = collection_id
        self.frames = frames_list.copy()
        self.fps = collection_fps

    def add_frame(self, frame) -> None:
        self.frames.append(frame)

    def delete_frame(self, frame) -> bool:
        if frame in self.frames:
            self.frames.remove(frame)
            return True
        return False

    def delete_frame_by_index(self, idx: int) -> bool:
        if 0 <= idx < len(self.frames):
            del self.frames[idx]
            return True
        return False

    def __repr__(self) -> str:
        return f"Collection(name={self.collection_name}, id={self.collection_id}, type={self.collection_type.value}, frames_count={len(self.frames)})"