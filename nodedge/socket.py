import logging
from collections import OrderedDict
from typing import Collection, List, NoReturn, Optional

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
        node: "Node",
        index: int = 0,
        position: int = LEFT_TOP,
        socketType: int = 1,
        allowsMultiEdges: bool = True,
        countOnThisNodeSide: int = 1,
        isInput: bool = False,
    ):
        super().__init__()
        self.node: "Node" = node
        self.index: int = index
        self.position: int = position
        self.countOnThisNodeSide: int = countOnThisNodeSide
        self.isInput: bool = isInput

        self.socketType: int = socketType
        self.allowsMultiEdges: bool = allowsMultiEdges

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.graphicsSocket: GraphicsSocket = GraphicsSocket(self, self.socketType)
        self.updateSocketPos()

        self.edges: List["Edge"] = []

    def __repr__(self):
        return f"0x{hex(id(self))[-4:]} Socket({self.index}, {self.position}, {self.socketType}, {self.allowsMultiEdges})"

    def updateSocketPos(self) -> NoReturn:
        self.graphicsSocket.setPos(
            *self.node.socketPos(self.index, self.position, self.countOnThisNodeSide)
        )

    def socketPos(self) -> Collection[float]:
        ret = self.node.socketPos(self.index, self.position, self.countOnThisNodeSide)
        self.__logger.debug(
            f"getSocketPos: {self.index}, {self.position}, {self.node}, {ret}"
        )

        return ret

    def addEdge(self, edge: Optional["Edge"] = None) -> NoReturn:
        if edge not in self.edges:
            self.edges.append(edge)

    def removeEdge(self, edgeToRemove: "Edge") -> NoReturn:
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

    def removeAllEdges(self) -> NoReturn:
        while self.edges:
            edge: "Edge" = self.edges.pop(0)
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
