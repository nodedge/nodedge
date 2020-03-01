# -*- coding: utf-8 -*-
"""
A module containing Nodedge's class for representing Socket and Socket Position Constants.
"""

import logging
from collections import OrderedDict
from enum import IntEnum
from typing import List, Optional, cast

from nodedge.graphics_socket import GraphicsSocket
from nodedge.serializable import Serializable


class SocketPosition(IntEnum):
    LEFT_TOP = 1  #:
    LEFT_CENTER = 2  #:
    LEFT_BOTTOM = 3  #:
    RIGHT_TOP = 4  #:
    RIGHT_CENTER = 5  #:
    RIGHT_BOTTOM = 6  #:


class Socket(Serializable):
    """Class representing Socket."""

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
        """
        :param node: reference to the :class:`~nodedge.node.Node` containing this `Socket`
        :type node: :class:`~nodedge.node.Node`
        :param index: Current index of this socket in the position
        :type index: ``int``
        :param position: Socket position
        :type position: :class:`~nodedge.socket.SocketPosition`
        :param socket_type: Constant defining type(color) of this socket
        :param multi_edges: Can this socket have multiple `Edges` connected?
        :type multi_edges: ``bool``
        :param count_on_this_node_side: number of total sockets on this position
        :type count_on_this_node_side: ``int``
        :param is_input: Is this an input `Socket`?
        :type is_input: ``bool``

        :Instance Attributes:

            - **node** - reference to the :class:`~nodedge.node.Node` containing this `Socket`
            - **edges** - list of `Edges` connected to this `Socket`
            - **grSocket** - reference to the :class:`~nodedge.graphics_socket.QDMGraphicsSocket`
            - **position** - Socket position. See :class:`~nodedge.socket.SocketPosition`
            - **index** - Current index of this socket in the position
            - **socket_type** - Constant defining type(color) of this socket
            - **count_on_this_node_side** - number of sockets on this position
            - **is_multi_edges** - ``True`` if `Socket` can contain multiple `Edges`
            - **is_input** - ``True`` if this socket serves for Input
            - **is_output** - ``True`` if this socket serves for Output
        """
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
        """Helper function to set `Graphics Socket` position. Exact socket position is calculated
                inside :class:`~nodedge.node.Node`."""

        self.graphicsSocket.setPos(
            *self.node.socketPos(self.index, self.position, self.countOnThisNodeSide)
        )

    def socketPos(self) -> List[float]:
        """
        :return: Returns this `Socket` position according the implementation stored in
            :class:`~nodedge.node.Node`
        :rtype: ``x, y`` position
        """

        ret = self.node.socketPos(self.index, self.position, self.countOnThisNodeSide)
        self.__logger.debug(
            f"getSocketPos: {self.index}, {self.position}, {self.node}, {ret}"
        )

        return cast(List, ret)

    # noinspection PyUnresolvedReferences
    def addEdge(self, edge: Optional["Edge"] = None) -> None:  # type: ignore # noqa: F821
        """
        Append an Edge to the list of connected Edges

        :param edge: :class:`~nodedge.edge.Edge` to connect to this `Socket`
        :type edge: :class:`~nodedge.edge.Edge`
        """

        if edge not in self.edges:
            self.edges.append(edge)

    # noinspection PyUnresolvedReferences
    def removeEdge(self, edgeToRemove: "Edge") -> None:  # type: ignore # noqa: F821
        """
        Disconnect passed :class:`~nodedge.edge.Edge` from this `Socket`
        :param edgeToRemove: :class:`~nodedge.edge.Edge` to disconnect
        :type edgeToRemove: :class:`~nodedge.edge.Edge`
        """
        if edgeToRemove in self.edges:
            self.edges.remove(edgeToRemove)
        else:
            self.__logger.debug(f"Trying to remove {edgeToRemove} from {self}.")

    def determineAllowsMultiEdges(self, data):
        """
        Deserialization helper function. In our tutorials we create new version of graph data format.
        This function is here to help solve the issue of opening older files in the newer format.
        If the 'multi_edges' param is missing in the dictionary, we determine if this `Socket`
        should support multiple `Edges`.

        :param data: `Socket` data in ``dict`` format for deserialization
        :type data: ``dict``
        :return: ``True`` if this `Socket` should support multi_edges
        """
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
        """Disconnect all `Edges` from this `Socket`"""
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
                ("position", self.position),
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
