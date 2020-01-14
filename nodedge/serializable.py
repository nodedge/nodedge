class Serializable:
    def __init__(self):
        self.id = id(self)

    def serialize(self):
        raise NotImplementedError()

    def deserialize(self, data, hashmap={}, restoreId=True):
        raise NotImplementedError()
