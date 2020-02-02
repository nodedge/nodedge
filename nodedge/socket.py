import logging
from collections import OrderedDict
from enum import IntEnum
from typing import List, Optional, cast

from nodedge.graphics_socket import GraphicsSocket
from nodedge.serializable import Serializable


class SocketPosition(IntEnum):
    LEFT_TOP = 1
    LEFT_CENTER = 2
    LEFT_BOTTOM = 3
    RIGHT_TOP = 4
    RIGHT_CENTER = 5
    RIGHT_BOTTOM = 6


class Socket(Serializable):
    def __init__(
        self,
        node: "Node",  # type: ignore # noqa: F821
        index: int = 0,
        position: int = SocketPosition.LEFT_TOP,
        socketType: int = 1,
        allowsMultiEdges: bool = True,
        countOnThisNodeSide: int = 1,
        isInput: bool = False,
    ):
        super().__init__()
        self.node: "Node" = node  # type: ignore # noqa: F821
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

        self.edges: List["Edge"] = []  # type: ignore

    def __repr__(self):
        return (
            f"0x{hex(id(self))[-4:]} Socket({self.index}, "
            f"{self.position}, {self.socketType}, {self.allowsMultiEdges})"
        )

    def updateSocketPos(self) -> None:
        self.graphicsSocket.setPos(
            *self.node.socketPos(self.index, self.position, self.countOnThisNodeSide)
        )

    def socketPos(self) -> List[float]:
        ret = self.node.socketPos(self.index, self.position, self.countOnThisNodeSide)
        self.__logger.debug(
            f"getSocketPos: {self.index}, {self.position}, {self.node}, {ret}"
        )

        return cast(List, ret)

    # noinspection PyUnresolvedReferences
    def addEdge(self, edge: Optional["Edge"] = None) -> None:  # type: ignore # noqa: F821
        if edge not in self.edges:
            self.edges.append(edge)

    # noinspection PyUnresolvedReferences
    def removeEdge(self, edgeToRemove: "Edge") -> None:  # type: ignore # noqa: F821
        if edgeToRemove in self.edges:
            self.edges.remove(edgeToRemove)
        else:
            self.__logger.debug(f"Trying to remove {edgeToRemove} from {self}.")

    def determineAllowsMultiEdges(self, data):
        if "allowsMultiEdges" in data:
            return data["allowsMultiEdges"]
        else:
            # Probably older version of file, make right socket multi edged by default
            return data["position"] in (
                SocketPosition.RIGHT_BOTTOM,
                SocketPosition.RIGHT_TOP,
            )

    # noinspection PyUnresolvedReferences
    def removeAllEdges(self) -> None:
        while self.edges:
            edge: "Edge" = self.edges.pop(0)  # type: ignore # noqa: F821
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

    def deserialize(self, data, hashmap=None, restoreId=True):
        if hashmap is None:
            hashmap = {}

        if restoreId:
            self.id = data["id"]
        self.allowsMultiEdges = data["allowsMultiEdges"]
        hashmap[data["id"]] = self

        return True
