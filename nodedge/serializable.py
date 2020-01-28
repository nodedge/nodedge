class Serializable:
    def __init__(self):
        self.id = id(self)

    def serialize(self):
        raise NotImplementedError()

    def deserialize(self, data, hashmap=None, restoreId=True):
        if hashmap is None:
            hashmap = {}
        raise NotImplementedError()
