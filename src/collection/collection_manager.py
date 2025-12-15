import threading
from typing import Dict, Optional

from src.collection.collection import Collection, CollectionType

class CollectionManager:
    _COLLECTIONS: Dict[int, Collection] = {}
    _COLLECTION_ID: int = 0
    _lock = threading.Lock()

    @classmethod
    def get_all_collections(cls) -> Dict[int, Collection]:
        return cls._COLLECTIONS

    @classmethod
    def create_collection(cls, collection_name: str = None, frames_list: list = None, collection_type: CollectionType = None) -> Collection:
        if collection_name is None:
            collection_name = f'Empty Collection {cls._COLLECTION_ID}'

        if frames_list is None:
            frames_list = []

        if collection_type is None:
            collection_type = CollectionType.CUSTOM

        with cls._lock:
            collection_id = cls._COLLECTION_ID
            ret = Collection(
                collection_name=collection_name,
                frames_list=frames_list,
                collection_type=collection_type,
                collection_id=collection_id
            )
            cls._COLLECTIONS[collection_id] = ret
            cls._COLLECTION_ID += 1
        return ret

    @classmethod
    def get_collection(cls, collection_id: int) -> Optional[Collection]:
        return cls._COLLECTIONS.get(collection_id)

    @classmethod
    def add_collection(cls, collection: Collection) -> bool:
        if not isinstance(collection, Collection):
            raise TypeError("只能添加Collection类型的实例")
        with cls._lock:
            if collection.collection_id in cls._COLLECTIONS:
                print(f"警告：Collection ID {collection.collection_id} 已存在，跳过添加")
                return False
            cls._COLLECTIONS[collection.collection_id] = collection
        return True

    @classmethod
    def remove_collection(cls, collection: Collection) -> bool:
        with cls._lock:
            if collection.collection_id in cls._COLLECTIONS:
                cls._COLLECTIONS.pop(collection.collection_id)
                return True
        return False

    @classmethod
    def clear_all(cls) -> None:
        with cls._lock:
            cls._COLLECTIONS.clear()
            cls._COLLECTION_ID = 0