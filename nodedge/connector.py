# -*- coding: utf-8 -*-
"""
Socket module containing Nodedge class for representing
:class:`~nodedge.socket.Socket` class and :class:`~nodedge.socket.SocketLocation`
constants.
"""

import logging
from collections import OrderedDict
from enum import IntEnum
from typing import List, Optional

from PySide6.QtCore import QPointF

from nodedge.graphics_socket import GraphicsSocket
from nodedge.serializable import Serializable
from nodedge.socket_type import SocketType


class SocketLocation(IntEnum):
    LEFT_TOP = 1  #: Left top
    LEFT_CENTER = 2  #: Left center
    LEFT_BOTTOM = 3  #: Left bottom
    RIGHT_TOP = 4  #: Right top
    RIGHT_CENTER = 5  #: Right center
    RIGHT_BOTTOM = 6  #: Right bottom


class Socket(Serializable):
    """
    Class representing input/output sockets of the nodes.
    """

    GraphicsSocketClass = GraphicsSocket

    def __init__(
        self,
        node: "Node",  # type: ignore # noqa: F821
        index: int = 0,
        location: int = SocketLocation.LEFT_TOP,
        socketType: SocketType = SocketType.Any,
        allowMultiEdges: bool = True,
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
        :param allowMultiEdges: attribute that defines if this socket
            can have multiple connected edges
        :type allowMultiEdges: ``bool``
        :param countOnThisNodeSide: number of total sockets on this socket side, i.e.
            input/output
        :type countOnThisNodeSide: ``int``
        :param isInput: attribute that defines whether this is an input or an
            output socket
        :type isInput: ``bool``
        """
        super().__init__()
        self.node: "Node" = node  # type: ignore # noqa: F821
        self.index: int = index
        self.location: int = location
        self.countOnThisNodeSide: int = countOnThisNodeSide
        self.isInput: bool = isInput

        self._socketType: SocketType = socketType
        self.allowMultiEdges: bool = allowMultiEdges

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.graphicsSocket: GraphicsSocket = self.__class__.GraphicsSocketClass(self)
        self.updateSocketPos()

        self.edges: List["Edge"] = []  # type: ignore

    @property
    def socketType(self) -> SocketType:
        return self._socketType

    @socketType.setter
    def socketType(self, newValue: SocketType):
        """
        Change the socket type

        :param newValue: new socket type
        :type newValue: ``int``
        """
        if self._socketType != newValue:
            self._socketType = newValue
            self.graphicsSocket.updateSocketType()

    @property
    def isOutput(self):
        """
        :getter: Return `True` is the :class:`~nodedge.socket.Socket` is not an input,
            `False` otherwise.
        :rtype: ``bool``
        """
        return not self.isInput

    @property
    def hasAnyEdge(self) -> bool:
        """
        Whether the :class:`~nodedge.socket.Socket` has any
        :class:`~nodedge.edge.Edge` connected to it.

        :return: ``True`` if any :class:`~nodedge.edge.Edge` is connected to this
            :class:`~nodedge.socket.Socket`
        :rtype: ``bool``
        """
        return len(self.edges) > 0

    @property
    def pos(self) -> QPointF:
        """
        :return: return this socket's position according the implementation stored in
            :class:`~nodedge.node.Node`
        :rtype: ``x, y`` position
        """

        ret: QPointF = self.node.socketPos(
            self.index, self.location, self.countOnThisNodeSide
        )
        return ret

    def delete(self):
        """
        Delete this :class:`~nodedge.socket.Socket`
        from :class:`~nodedge.scene.Scene`.
        """
        self.graphicsSocket.setParentItem(None)
        self.node.scene.grScene.removeItem(self.graphicsSocket)
        del self.graphicsSocket

    def __repr__(self):
        return (
            f"0x{hex(id(self))[-4:]} Socket({self.index}, "
            f"{self.location}, {self.socketType}, {self.allowMultiEdges})"
        )

    def isConnected(self, edge: "Edge") -> bool:  # type: ignore
        """
        Returns ``True`` if :class:`~nodedge.edge.Edge` is connected to this
        :class:`~nodedge.socket.Socket`.

        :param edge: :class:`~nodedge.edge.Edge` to check if it is connected to this
            :class:`~nodedge.socket.Socket`
        :type edge: :class:`~nodedge.edge.Edge`
        :return: ``True`` if :class:`~nodedge.edge.Edge` is connected to this socket
        :rtype: ``bool``
        """
        return edge in self.edges

    def updateSocketPos(self) -> None:
        """
        Helper function to set the graphical socket position.
        The exact socket position is calculated inside :class:`~nodedge.node.Node`.
        """

        socketPos = self.node.socketPos(
            self.index, self.location, self.countOnThisNodeSide
        )
        self.graphicsSocket.setPos(socketPos)

    # noinspection PyUnresolvedReferences
    def addEdge(self, edge: Optional["Edge"] = None) -> None:  # type: ignore # noqa: F821
        """
        Append an :class:`~nodedge.edge.Edge` to the list of the connected
        :class:`~nodedge.edge.Edge`.

        :param edge: :class:`~nodedge.edge.Edge` to connect to this
            :class:`~nodedge.socket.Socket`
        :type edge: :class:`~nodedge.edge.Edge`
        """

        if edge not in self.edges:
            self.edges.append(edge)

    # noinspection PyUnresolvedReferences
    def removeEdge(self, edgeToRemove: "Edge") -> None:  # type: ignore # noqa: F821
        """
        Disconnect passed :class:`~nodedge.edge.Edge` from
        this :class:`~nodedge.socket.Socket`.

        :param edgeToRemove: :class:`~nodedge.edge.Edge` to disconnect
        :type edgeToRemove: :class:`~nodedge.edge.Edge`
        """
        if edgeToRemove in self.edges:
            self.edges.remove(edgeToRemove)
        else:
            self.__logger.debug(f"Trying to remove {edgeToRemove} from {self}.")

    # noinspection PyUnresolvedReferences
    def removeAllEdges(self, silent=False) -> None:
        """
        Disconnect all :class:`~nodedge.edge.Edge` from
        this :class:`~nodedge.socket.Socket`.

        :param silent: If true, remove the edge without notifications
        :type silent: ``bool``
        """
        while self.edges:
            edge: "Edge" = self.edges.pop(0)  # type: ignore # noqa: F821
            self.__logger.debug(f"Removing {edge} from {self}")
            if silent:
                edge.remove(silent)
            else:
                edge.remove()

    @staticmethod
    def determineAllowMultiEdges(data):
        """
        Deserialization helper function.

        .. note::

            This function is here to help solve the issue of opening older files in
            the newer format.

        If the `allowMultiEdges` param is missing in the dictionary, we determine if
        this :class:`~nodedge.socket.Socket` should support multiple
        :class:`~nodedge.edge.Edge`.

        :param data: socket's data in ``dict`` format for deserialization
        :type data: ``dict``
        :return: ``True`` if this socket should support multiple edges
        """
        if "allowMultiEdges" in data:
            return data["allowMultiEdges"]
        else:
            # Probably older version of file, make right socket multi edged by default
            return data["location"] in (
                SocketLocation.RIGHT_BOTTOM,
                SocketLocation.RIGHT_TOP,
            )

    def serialize(self) -> OrderedDict:
        return OrderedDict(
            [
                ("id", self.id),
                ("index", self.index),
                ("allowMultiEdges", self.allowMultiEdges),
                ("location", self.location),
                ("socketType", self.socketType.value),
            ]
        )

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = True,
        *args,
        **kwargs,
    ):
        if hashmap is None:
            hashmap = {}

        if restoreId:
            self.id = data["id"]
        self.allowMultiEdges = data["allowMultiEdges"]
        self.socketType = SocketType(data["socketType"])
        self.location = data["location"]
        hashmap[data["id"]] = self

        return True
