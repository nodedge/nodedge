# -*- coding: utf-8 -*-
"""
Node content module containing Nodedge's class for representing :class:`~nodedge.socket.Socket` class and
:class:`~nodedge.socket.SocketLocation` constants.
"""

import logging
from collections import OrderedDict
from enum import IntEnum
from typing import List, Optional, cast

from nodedge.graphics_socket import GraphicsSocket
from nodedge.serializable import Serializable


class SocketLocation(IntEnum):
    LEFT_TOP = 1  #:
    LEFT_CENTER = 2  #:
    LEFT_BOTTOM = 3  #:
    RIGHT_TOP = 4  #:
    RIGHT_CENTER = 5  #:
    RIGHT_BOTTOM = 6  #:


class Socket(Serializable):
    """
    Class representing input/output sockets of the nodes.
    """

    def __init__(
        self,
        node: "Node",  # type: ignore # noqa: F821
        index: int = 0,
        location: int = SocketLocation.LEFT_TOP,
        socketType: int = 1,
        allowsMultiEdges: bool = True,
        countOnThisNodeSide: int = 1,
        isInput: bool = False,
    ):
        """
        :param node: reference to the :class:`~nodedge.node.Node` containing this socket
        :type node: :class:`~nodedge.node.Node`
        :param index: current index of this socket in the position
        :type index: ``int``
        :param location: socket position
        :type location: :class:`~nodedge.socket.SocketLocation`
        :param socketType: constant defining type of this socket. Every type is visually
            associated to a color.
        :param allowsMultiEdges: attribute that defines if this socket
            can have multiple connected edges
        :type allowsMultiEdges: ``bool``
        :param countOnThisNodeSide: number of total sockets on this socket side, i.e. input/output
        :type countOnThisNodeSide: ``int``
        :param isInput: attribute that defines whether this is an input or an output socket
        :type isInput: ``bool``
        """
        super().__init__()
        self.node: "Node" = node  # type: ignore # noqa: F821
        self.index: int = index
        self.location: int = location
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
            f"{self.location}, {self.socketType}, {self.allowsMultiEdges})"
        )

    def updateSocketPos(self) -> None:
        """
        Helper function to set the graphical socket position.
        The exact socket position is calculated inside :class:`~nodedge.node.Node`.
        """

        socketPos = self.node.socketPos(
            self.index, self.location, self.countOnThisNodeSide
        )
        self.graphicsSocket.setPos(socketPos)

    def socketPos(self) -> List[float]:
        """
        :return: return this socket's position according the implementation stored in
            :class:`~nodedge.node.Node`
        :rtype: ``x, y`` position
        """

        ret = self.node.socketPos(self.index, self.location, self.countOnThisNodeSide)
        self.__logger.debug(
            f"getSocketPos: {self.index}, {self.location}, {self.node}, {ret}"
        )

        return cast(List, ret)

    # noinspection PyUnresolvedReferences
    def addEdge(self, edge: Optional["Edge"] = None) -> None:  # type: ignore # noqa: F821
        """
        Append an edge to the list of the connected edges.

        :param edge: :class:`~nodedge.edge.Edge` to connect to this socket
        :type edge: :class:`~nodedge.edge.Edge`
        """

        if edge not in self.edges:
            self.edges.append(edge)

    # noinspection PyUnresolvedReferences
    def removeEdge(self, edgeToRemove: "Edge") -> None:  # type: ignore # noqa: F821
        """
        Disconnect passed :class:`~nodedge.edge.Edge` from this socket
        :param edgeToRemove: :class:`~nodedge.edge.Edge` to disconnect
        :type edgeToRemove: :class:`~nodedge.edge.Edge`
        """
        if edgeToRemove in self.edges:
            self.edges.remove(edgeToRemove)
        else:
            self.__logger.debug(f"Trying to remove {edgeToRemove} from {self}.")

    def determineAllowsMultiEdges(self, data):
        """
        Deserialization helper function.

        .. note::

            This function is here to help solve the issue of opening older files in the newer format.

        If the 'multi_edges' param is missing in the dictionary, we determine if this `Socket`
        should support multiple `Edges`.

        :param data: socket's data in ``dict`` format for deserialization
        :type data: ``dict``
        :return: ``True`` if this socket should support multiple edges
        """
        if "allowsMultiEdges" in data:
            return data["allowsMultiEdges"]
        else:
            # Probably older version of file, make right socket multi edged by default
            return data["position"] in (
                SocketLocation.RIGHT_BOTTOM,
                SocketLocation.RIGHT_TOP,
            )

    # noinspection PyUnresolvedReferences
    def removeAllEdges(self) -> None:
        """
        Disconnect all edges from this socket.
        """
        while self.edges:
            edge: "Edge" = self.edges.pop(0)  # type: ignore # noqa: F821
            self.__logger.debug(f"Removing {edge} from {self}")
            edge.remove()

    def serialize(self) -> OrderedDict:
        return OrderedDict(
            [
                ("id", self.id),
                ("index", self.index),
                ("allowsMultiEdges", self.allowsMultiEdges),
                ("position", self.location),
                ("socketType", self.socketType),
            ]
        )

    def deserialize(
        self, data: dict, hashmap: Optional[dict] = None, restoreId: bool = True
    ) -> bool:
        if hashmap is None:
            hashmap = {}

        if restoreId:
            self.id = data["id"]
        self.allowsMultiEdges = data["allowsMultiEdges"]
        hashmap[data["id"]] = self

        return True
