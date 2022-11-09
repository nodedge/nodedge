# -*- coding: utf-8 -*-
"""Edge module containing :class:`~nodedge.edge.Edge` and
:class:`~nodedge.edge.EdgeType` class. """

import logging
from collections import OrderedDict
from enum import IntEnum
from typing import Callable, List, Optional

from nodedge.connector import Socket
from nodedge.graphics_edge import (
    GraphicsEdge,
    GraphicsEdgeBezier,
    GraphicsEdgeCircuit,
    GraphicsEdgeDirect,
)
from nodedge.serializable import Serializable
from nodedge.utils import dumpException


class EdgeType(IntEnum):
    """
    Edge Type Constants
    """

    STRAIGHT = 1  #:
    BEZIER = 2  #:
    CIRCUIT = 3  #:


class Edge(Serializable):
    """
    Edge class.

    The edge is the component connecting two :class:`~nodedge.node.Node` s.

    [NODE 1]------EDGE------[NODE 2]
    """

    edgeValidators: List[Callable] = []  #: class variable containing list of
    # registered edge validators

    def __init__(
        self,
        scene: "Scene",  # type: ignore
        startSocket: Optional[Socket] = None,
        endSocket: Optional[Socket] = None,
        edgeType: EdgeType = EdgeType.CIRCUIT,
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
            - **graphicsEdge**
            - Instance of :class:`~nodedge.graphics_edge.GraphicsEdge` subclass
                handling graphical representation in the ``QGraphicsScene``.
        """

        super().__init__()

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        # Default initialization
        self._sourceSocket: Optional[Socket] = None
        self._targetSocket: Optional[Socket] = None

        self.scene: "Scene" = scene  # type: ignore
        self.sourceSocket: Socket = startSocket
        self.targetSocket: Socket = endSocket
        self._edgeType: EdgeType = edgeType
        self.edgeType: EdgeType = edgeType

        self.scene.addEdge(self)

    def __str__(self) -> str:
        """
        :return: Edge(hex id, start socket hex id, end socket hex id, edge type)
        :rtype: ``string``
        """
        return (
            f"0x{hex(id(self))[-4:]} Edge(0x{hex(id(self.sourceSocket))[-4:]}, "
            f"0x{hex(id(self.targetSocket))[-4:]}, "
            f"{self.edgeType})"
        )

    @property
    def sourceSocket(self) -> Optional[Socket]:
        """
        Source socket.

        :getter: Return source :class:`~nodedge.socket.Socket`.
        :setter: Set source :class:`~nodedge.socket.Socket` safely.
        :type: :class:`~nodedge.socket.Socket`
        """
        return self._sourceSocket

    @sourceSocket.setter
    def sourceSocket(self, value: Socket) -> None:
        # If the edge was assigned to another socket before, remove the edge from the
        # socket.
        if self._sourceSocket is not None:
            self._sourceSocket.removeEdge(self)
        # Assign new start socket.
        self._sourceSocket = value
        # Add edge to the socket class.
        if self.sourceSocket is not None:
            self.sourceSocket.addEdge(self)

    @property
    def targetSocket(self) -> Optional[Socket]:
        """
        Target socket

        :getter: Return target :class:`~nodedge.socket.Socket` or ``None`` if not set.
        :setter: Set target :class:`~nodedge.socket.Socket` safely.
        :type: :class:`~nodedge.socket.Socket` or ``None``
        """
        return self._targetSocket

    @targetSocket.setter
    def targetSocket(self, value: Socket) -> None:
        # If the edge was assigned to another socket before, remove the edge from the
        # socket.
        if self._targetSocket is not None:
            self._targetSocket.removeEdge(self)
        # Assign new end socket.
        self._targetSocket = value
        # Add edge to the socket class.
        if self.targetSocket is not None:
            self.targetSocket.addEdge(self)

    @property
    def edgeType(self) -> int:
        """
        Edge type

        :getter: Get edge type constant for current :class:`~nodedge.edge.Edge`.
        :setter: Set new edge type. On background, create new
            :class:`~nodedge.graphics_edge.GraphicsEdge` child class if necessary,
            add this ``QGraphicsPathItem`` to the ``QGraphicsScene`` and update edge
            sockets positions.
        :type: :class:`~nodedge.edge.EdgeType`
        """
        return self._edgeType

    @edgeType.setter
    def edgeType(self, value: EdgeType) -> None:
        if hasattr(self, "graphicsEdge") and self.graphicsEdge is not None:
            self.scene.graphicsScene.removeItem(self.graphicsEdge)

        self._edgeType = value

        if self.edgeType == EdgeType.STRAIGHT:
            self.graphicsEdge: GraphicsEdge = GraphicsEdgeDirect(self)
        elif self.edgeType == EdgeType.BEZIER:
            self.graphicsEdge = GraphicsEdgeBezier(self)
        else:
            self.graphicsEdge = GraphicsEdgeCircuit(self)
        self.scene.graphicsScene.addItem(self.graphicsEdge)

        if self.sourceSocket is not None:
            self.updatePos()

    @property
    def isSelected(self):
        """
        Property defining whether the edge is selected or not.

        :getter: Get selection state of the edge.
        :setter: Provide the safe selecting/deselecting operation. In the background it
            takes care about the flags, notifications and storing history for undo/redo.

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
        Update the internal :class:`~nodedge.graphics_edge.GraphicsEdge` positions
        according to the start and end :class:`~nodedge.socket.Socket`
        """

        sourcePos = None
        if self.sourceSocket is not None:
            sourcePos = (
                self.sourceSocket.pos + self.sourceSocket.node.graphicsNode.pos()
            )
            if self.graphicsEdge is not None:
                self.graphicsEdge.sourcePos = sourcePos

        if self.targetSocket is not None:
            targetPos = (
                self.targetSocket.pos + self.targetSocket.node.graphicsNode.pos()
            )
            if self.graphicsEdge is not None:
                self.graphicsEdge.targetPos = targetPos
        else:
            if self.graphicsEdge is not None:
                if sourcePos is not None:
                    self.graphicsEdge.targetPos = sourcePos

        self.__logger.debug(f"Start socket: {self.sourceSocket}")
        self.__logger.debug(f"End socket: {self.targetSocket}")
        if self.graphicsEdge is not None:
            self.graphicsEdge.update()

    def getOtherSocket(self, knownSocket: Optional["Socket"]):
        """
        Return the opposite :class:`~nodedge.socket.Socket` on this
        :class:`~nodedge.edge.Edge`.

        :param knownSocket: Provide known :class:`~nodedge.socket.Socket` to be able
            to determine the opposite one
        :type knownSocket: :class:`~nodedge.socket.Socket`
        :return: The opposite socket on this :class:`~nodedge.edge.Edge`,
            eventually ``None``.
        :rtype: :class:`~nodedge.socket.Socket` or ``None``
        """

        return (
            self.sourceSocket if knownSocket == self.targetSocket else self.targetSocket
        )

    def removeFromSockets(self) -> None:
        """
        Set start and end :class:`~nodedge.socket.Socket` to ``None``
        """
        self.targetSocket = None
        self.sourceSocket = None

    def remove(self, silentForSocket: Optional[Socket] = None, silent: bool = False):
        """
        Safely remove this `Edge`.

        Remove :class:`~nodedge.graphics_edge.GraphicsEdge` from the
        ``QGraphicsScene`` and it's reference to all other graphical elements. Notify
        previously connected :class:`~nodedge.node.Node` (s) about this event.

        Triggered Node Slots:
        - :py:func:`~nodedge.node.Node.onEdgeConnectionChanged`
        - :py:func:`~nodedge.node.Node.onInputChanged`

        :param silentForSocket: Socket for whom the removal is silent
        :type silentForSocket: Optional[:class:`~nodedge.socket.Socket`]
        :param silent: ``True`` if no events should be triggered during removing
        :type silent: ``bool``
        """

        oldSockets = [self.sourceSocket, self.targetSocket]

        # ugly hack, since I noticed that even when you remove grEdge from scene,
        # sometimes it stays there! How dare you Qt!
        if self.graphicsEdge is not None:
            self.graphicsEdge.hide()

        self.__logger.debug(f"Removing {self} from all sockets.")
        self.removeFromSockets()

        self.__logger.debug(f"Removing Graphical edge: {self.graphicsEdge}")
        self.scene.graphicsScene.removeItem(self.graphicsEdge)
        self.scene.graphicsScene.update()
        self.graphicsEdge = None  # type: ignore

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
                    if silent:
                        continue
                    if silentForSocket is not None and socket == silentForSocket:
                        # if we requested silence for Socket and it's this one,
                        # skip notifications
                        continue

                    socket.node.onEdgeConnectionChanged(self)
                    if socket.isInput:
                        socket.node.onInputChanged(socket)
        except Exception as e:
            dumpException(e)

    @classmethod
    def getEdgeValidators(cls):
        """Return the list of Edge Validator Callbacks"""
        return cls.edgeValidators

    @classmethod
    def registerEdgeValidator(cls, validatorCallback: Callable):
        """Register Edge Validator Callback

        :param validatorCallback: A function handle to validate Edge
        :type validatorCallback: `function`
        """
        cls.edgeValidators.append(validatorCallback)

    @classmethod
    def validateEdge(cls, startSocket: Socket, endSocket: Socket) -> bool:
        """Validate Edge against all registered `Edge Validator Callbacks`

        :param startSocket: Starting :class:`~nodedge.socket.Socket` of Edge to check
        :type startSocket: :class:`~nodedge.socket.Socket`
        :param endSocket: Target/End :class:`~nodedge.socket.Socket` of Edge to check
        :type endSocket: :class:`~nodedge.socket.Socket`
        :return: ``True`` if the Edge is valid, ``False`` otherwise
        :rtype: ``bool``
        """
        for validator in cls.getEdgeValidators():
            if not validator(startSocket, endSocket):
                return False
        return True

    def reconnect(self, sourceSocket: Socket, targetSocket: Socket):
        """Helper function which reconnects edge `sourceSocket` to `targetSocket`"""
        if self.sourceSocket == sourceSocket:
            self.sourceSocket = targetSocket
        elif self.targetSocket == sourceSocket:
            self.targetSocket = targetSocket

    def serialize(self) -> OrderedDict:
        """
        Serialization method.

        :return: Serialized edge
        :rtype: ``OrderedDict``
        """
        return OrderedDict(
            [
                ("id", self.id),
                ("edgeType", self.edgeType),
                (
                    "source",
                    self.sourceSocket.id if self.sourceSocket is not None else None,
                ),
                (
                    "target",
                    self.targetSocket.id if self.targetSocket is not None else None,
                ),
            ]
        )

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = True,
        *args,
        **kwargs,
    ) -> bool:
        """
        Deserialization method.

        :param data:
        :type data: ``dict``
        :param hashmap:
        :type hashmap: ``Optional[dict]``
        :param restoreId:
        :type restoreId: ``bool``
        :return: success status
        :rtype: ``bool``
        """
        if hashmap is None:
            hashmap = {}
        if restoreId:
            self.id = data["id"]
        if data["source"]:
            self.sourceSocket = hashmap[data["source"]]
        if data["target"]:
            self.targetSocket = hashmap[data["target"]]
        self.edgeType = data["edgeType"]

        return True
