import logging
from collections import OrderedDict

from nodedge.ack_serializable import AckSerializable
from nodedge.ack_graphics_socket import AckGraphicsSocket


LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4


class AckSocket(AckSerializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socketType=1, allowsMultiEdges=True):
        super().__init__()
        self.node = node
        self.index = index
        self.position = position

        self.socketType = socketType
        self.allowsMultiEdges = allowsMultiEdges

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

        self.graphicsSocket = AckGraphicsSocket(self, self.socketType)
        self.graphicsSocket.setPos(*self.node.getSocketPos(index, position))

        self.edges = []

    def __repr__(self):
        return f"0x{hex(id(self))[-4:]} Socket({self.index}, {self.position}, {self.socketType}, {self.allowsMultiEdges})"

    def getSocketPos(self):
        ret = self.node.getSocketPos(self.index, self.position)
        self.__logger.debug(f"getSocketPos: {self.index}, {self.position}, {self.node}, {ret}")

        return ret

    def addEdge(self, edge=None):
        self.edges.append(edge)

    def removeEdge(self, edgeToRemove):
        if edgeToRemove in self.edges:
            self.edges.remove(edgeToRemove)
        else:
            self.__logger.warning(f"Trying to remove {edgeToRemove} from {self}.")

    def removeAllEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            self.__logger.debug(f"Removing {edge} from {self}")
            edge.remove()

    def serialize(self):
        return OrderedDict([("id",  self.id),
                            ("index",  self.index),
                            ("allowsMultiEdges", self.allowsMultiEdges),
                            ("position",  self.position),
                            ("socketType",  self.socketType)
                            ])

    def deserialize(self, data, hashmap={}, restoreId=True):
        if restoreId:
            self.id = data["id"]
        self.allowsMultiEdges = data["allowsMultiEdges"]
        hashmap[data["id"]] = self

        return True
