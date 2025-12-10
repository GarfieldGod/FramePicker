COLLECTIONS = {}

class CollectionManager:
    @staticmethod
    def get_collection(collection_id):
        return COLLECTIONS[collection_id]

    @staticmethod
    def add_collection(collection):
        if collection.collection_id not in COLLECTIONS:
            COLLECTIONS[collection.collection_id] = collection

    @staticmethod
    def remove_collection(collection):
        COLLECTIONS.pop(collection.collection_id)

class Collection:
    frames = []
    collection_id = None
    collection_type = None
    def __init__(self, frames_list, collection_type, collection_id):
        self.collection_id = collection_id
        self.frames = frames_list
        self.collection_type = collection_type

    def add_frame(self, frame):
        self.frames.append(frame)

    def delete_frame(self, frame):
        self.frames.remove(frame)