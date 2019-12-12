
class AckSerializable:
    def __init__(self):
        self.id = id(self)

    def serialize(self):
        raise NotImplemented()

    def deserialize(self, data, hashmap={}, restoreId=True):
        raise NotImplemented()
