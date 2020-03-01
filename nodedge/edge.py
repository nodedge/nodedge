# -*- coding: utf-8 -*-
"""
Edge module containing :class:`~nodedge.edge.Edge` and :class:`~nodedge.edge.EdgeType` class.
"""

import logging
from collections import OrderedDict
from enum import IntEnum
from typing import Optional

from nodedge.graphics_edge import GraphicsEdge, GraphicsEdgeBezier, GraphicsEdgeDirect
from nodedge.serializable import Serializable
from nodedge.socket import Socket
from nodedge.utils import dumpException


class EdgeType(IntEnum):
    """
    Edge Type Constants
    """

    DIRECT = 1  #:
    BEZIER = 2  #:


class Edge(Serializable):
    """
    Edge class.

    The edge is the component connecting two nodes.

    [NODE 1]------EDGE------[NODE 2]
    """

    def __init__(
        self,
        scene: "Scene",  # type: ignore
        startSocket: Optional[Socket] = None,
        endSocket: Optional[Socket] = None,
        edgeType: EdgeType = EdgeType.BEZIER,
    ):
        """
        :param scene: Reference to the scene
        :type scene: :class:`~nodedge.scene.Scene`
        :param startSocket: Reference to the starting socket
        :type startSocket: :class:`~nodedge.socket.Socket`
        :param  endSocket: Reference to the End socket or ``None``
        :type endSocket: :class:`~nodedge.socket.Socket` | ``None``
        :param edgeType: Constant determining type of edge.
        :type edgeType: :class:`~nodedge.edge.EdgeType`

        :Instance Attributes:

            - **scene** - reference to the :class:`~nodedge.scene.Scene`
            - **graphicsEdge** - Instance of :class:`~nodedge.graphics_edge.GraphicsEdge` subclass handling graphical representation in the ``QGraphicsScene``.
        """

        super().__init__()

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        # Default initialization
        self._sourceSocket: Optional[Socket] = None
        self._destinationSocket: Optional[Socket] = None

        self.scene: "Scene" = scene  # type: ignore
        self.sourceSocket: Socket = startSocket
        self.destinationSocket: Socket = endSocket
        self._edgeType: EdgeType = edgeType
        self.edgeType: EdgeType = edgeType

        self.scene.addEdge(self)

    def __str__(self):
        """

        :return: Edge(hex id, start socket hex id, end socket hex id, edge type)
        :rtype: ``string``
        """
        return (
            f"0x{hex(id(self))[-4:]} Edge(0x{hex(id(self.sourceSocket))[-4:]}, "
            f"0x{hex(id(self.destinationSocket))[-4:]}, "
            f"{self.edgeType})"
        )

    @property
    def sourceSocket(self) -> Optional[Socket]:
        """
        Start socket

        :getter: Return source :class:`~nodedge.socket.Socket`.
        :setter: Set source :class:`~nodedge.socket.Socket` safely.
        :type: :class:`~nodedge.socket.Socket`
        """
        return self._sourceSocket

    @sourceSocket.setter
    def sourceSocket(self, value: Socket) -> None:
        # If the edge was assigned to another socket before, remove the edge from the socket.
        if self._sourceSocket is not None:
            self._sourceSocket.removeEdge(self)
        # Assign new start socket.
        self._sourceSocket = value
        # Add edge to the socket class.
        if self.sourceSocket is not None:
            self.sourceSocket.addEdge(self)

    @property
    def destinationSocket(self) -> Optional[Socket]:
        """
        End socket

        :getter: Return destination :class:`~nodedge.socket.Socket` or ``None`` if not set.
        :setter: Set destination :class:`~nodedge.socket.Socket` safely.
        :type: :class:`~nodedge.socket.Socket` or ``None``
        """
        return self._destinationSocket

    @destinationSocket.setter
    def destinationSocket(self, value: Socket) -> None:
        # If the edge was assigned to another socket before, remove the edge from the socket.
        if self._destinationSocket is not None:
            self._destinationSocket.removeEdge(self)
        # Assign new end socket.
        self._destinationSocket = value
        # Add edge to the socket class.
        if self.destinationSocket is not None:
            self.destinationSocket.addEdge(self)

    @property
    def edgeType(self) -> int:
        """
        Edge type

        :getter: Get edge type constant for current ``Edge``.
        :setter: Set new edge type. On background, create new :class:`~nodedge.graphics_edge.GraphicsEdge`
            child class if necessary, add this ``QGraphicsPathItem`` to the ``QGraphicsScene`` and update edge sockets
            positions.
        :type: :class:`~nodedge.edge.EdgeTyoe`
        """
        return self._edgeType

    @edgeType.setter
    def edgeType(self, value: EdgeType) -> None:
        if hasattr(self, "graphicsEdge") and self.graphicsEdge is not None:
            self.scene.graphicsScene.removeItem(self.graphicsEdge)

        self._edgeType = value

        if self.edgeType == EdgeType.DIRECT:
            self.graphicsEdge: GraphicsEdge = GraphicsEdgeDirect(self)
        else:
            self.graphicsEdge = GraphicsEdgeBezier(self)
        self.scene.graphicsScene.addItem(self.graphicsEdge)

        if self.sourceSocket is not None:
            self.updatePos()

    @property
    def isSelected(self):
        """
        Property defining whether the edge is selected or not.

        :getter: Get selection state of the edge.
        :setter: Provide the safe selecting/deselecting operation. In the background it takes care about the flags,
            notifications and storing history for undo/redo.

        :type: ``bool``
        """
        return self.graphicsEdge.isSelected()

    @isSelected.setter
    def isSelected(self, value: bool):
        self.graphicsEdge.setSelected(value)
        self.graphicsEdge._lastSelectedState = value
        if value is True:
            self.graphicsEdge.onSelected()

    def updatePos(self) -> None:
        """
        Update the internal :class:`~nodedge.graphics_edge.GraphicsEdge` positions according to the
        start and end :class:`~nodedge.socket.Socket`
        """

        if self.sourceSocket is not None:
            sourcePos = (
                self.sourceSocket.socketPos()
                + self.sourceSocket.node.graphicsNode.pos()
            )
            if self.graphicsEdge is not None:
                self.graphicsEdge.sourcePos = sourcePos
        # TODO: simplify terminology: end -> destination | start -> source

        if self.destinationSocket is not None:
            destinationPos = (
                self.destinationSocket.socketPos()
                + self.destinationSocket.node.graphicsNode.pos()
            )
            if self.graphicsEdge is not None:
                self.graphicsEdge.destinationPos = destinationPos
        else:
            if self.graphicsEdge is not None:
                self.graphicsEdge.destinationPos = sourcePos

        self.__logger.debug(f"Start socket: {self.sourceSocket}")
        self.__logger.debug(f"End socket: {self.destinationSocket}")
        if self.graphicsEdge is not None:
            self.graphicsEdge.update()

    def getOtherSocket(self, knownSocket: "Socket"):
        """
        Return the opposite socket on this `Edge`.

        :param knownSocket: Provide known :class:`~nodedge.socket.Socket` to be able to determine the opposite one
        :type knownSocket: :class:`~nodedge.socket.Socket`
        :return: The opposite socket on this ``Edge``, eventually ``None``
        :rtype: :class:`~nodedge.socket.Socket` or ``None``
        """

        return (
            self.sourceSocket
            if knownSocket == self.destinationSocket
            else self.destinationSocket
        )

    def removeFromSockets(self):
        """
        Set start and end :class:`~nodedge.socket.Socket` to ``None``
        """

        # TODO: Is it meaningful?
        self.destinationSocket = None
        self.sourceSocket = None

    def remove(self):
        """
        Safely remove this `Edge`.

        Remove :class:`~nodedge.graphics_edge.GraphicsEdge` from the ``QGraphicsScene`` and it's reference to all other
        graphical elements.
        Notify previously connected :class:`~nodedge.node.Node` (s) about this event.

        Triggered Node Slots:
        - :py:meth:`~nodedge.node.Node.onEdgeConnectionChanged`
        - :py:meth:`~nodedge.node.Node.onInputChanged`
        """

        oldSockets = [self.sourceSocket, self.destinationSocket]

        self.__logger.debug(f"Removing {self} from all sockets.")
        self.removeFromSockets()

        self.__logger.debug(f"Removing Graphical edge: {self.graphicsEdge}")
        self.scene.graphicsScene.removeItem(self.graphicsEdge)
        self.graphicsEdge = None

        self.__logger.debug(f"Removing {self}")
        try:
            self.scene.removeEdge(self)
        except ValueError as e:
            self.__logger.debug(e)

        self.__logger.debug("Edge has been deleted.")

        # Notify nodes from old sockets
        try:
            for socket in oldSockets:
                if socket is not None and socket.node is not None:
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.isInput:
                        socket.node.onInputChanged(self)
        except Exception as e:
            dumpException(e)

    def serialize(self):
        return OrderedDict(
            [
                ("id", self.id),
                ("edgeType", self.edgeType),
                ("sourceSocket", self.sourceSocket.id),
                (
                    "destinationSocket",
                    self.destinationSocket.id
                    if self.destinationSocket is not None
                    else None,
                ),
            ]
        )

    def deserialize(self, data, hashmap=None, restoreId=True):
        if hashmap is None:
            hashmap = {}
        if restoreId:
            self.id = data["id"]
        self.sourceSocket = hashmap[data["sourceSocket"]]
        self.destinationSocket = hashmap[data["destinationSocket"]]
        self.edgeType = data["edgeType"]

        return True
