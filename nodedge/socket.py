import logging
from collections import OrderedDict

from nodedge.graphics_socket import GraphicsSocket
from nodedge.serializable import Serializable

LEFT_TOP = 1
LEFT_CENTER = 2
LEFT_BOTTOM = 3
RIGHT_TOP = 4
RIGHT_CENTER = 5
RIGHT_BOTTOM = 6


class Socket(Serializable):
    def __init__(
        self,
        node,
        index=0,
        position=LEFT_TOP,
        socketType=1,
        allowsMultiEdges=True,
        countOnThisNodeSide=1,
        isInput=False,
    ):
        super().__init__()
        self.node = node
        self.index = index
        self.position = position
        self.countOnThisNodeSide = countOnThisNodeSide
        self.isInput = isInput

        self.socketType = socketType
        self.allowsMultiEdges = allowsMultiEdges

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.graphicsSocket = GraphicsSocket(self, self.socketType)
        self.updateSocketPos()

        self.edges = []

    def __repr__(self):
        return f"0x{hex(id(self))[-4:]} Socket({self.index}, {self.position}, {self.socketType}, {self.allowsMultiEdges})"

    def updateSocketPos(self):
        self.graphicsSocket.setPos(
            *self.node.socketPos(self.index, self.position, self.countOnThisNodeSide)
        )

    def socketPos(self):
        ret = self.node.socketPos(self.index, self.position, self.countOnThisNodeSide)
        self.__logger.debug(
            f"getSocketPos: {self.index}, {self.position}, {self.node}, {ret}"
        )

        return ret

    def addEdge(self, edge=None):
        if edge not in self.edges:
            self.edges.append(edge)

    def removeEdge(self, edgeToRemove):
        if edgeToRemove in self.edges:
            self.edges.remove(edgeToRemove)
        else:
            self.__logger.warning(f"Trying to remove {edgeToRemove} from {self}.")

    def determineAllowsMultiEdges(self, data):
        if "allowsMultiEdges" in data:
            return data["allowsMultiEdges"]
        else:
            # Probably older version of file, make right socket multiedged by default
            return data["position"] in (RIGHT_BOTTOM, RIGHT_TOP)

    def removeAllEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            self.__logger.debug(f"Removing {edge} from {self}")
            edge.remove()

    def serialize(self):
        return OrderedDict(
            [
                ("id", self.id),
                ("index", self.index),
                ("allowsMultiEdges", self.allowsMultiEdges),
                ("position", self.position),
                ("socketType", self.socketType),
            ]
        )

    def deserialize(self, data, hashmap={}, restoreId=True):
        if restoreId:
            self.id = data["id"]
        self.allowsMultiEdges = data["allowsMultiEdges"]
        hashmap[data["id"]] = self

        return True
