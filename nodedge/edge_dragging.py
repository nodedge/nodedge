# -*- coding: utf-8 -*-
"""
Edge dragging module containing :class:`~nodedge.edge_dragging.EdgeDragging` class.
"""

import logging
from enum import IntEnum
from typing import Optional

from PySide6.QtWidgets import QGraphicsItem

from nodedge.connector import Socket
from nodedge.edge import Edge, EdgeType
from nodedge.graphics_socket import GraphicsSocket
from nodedge.utils import dumpException


class EdgeDraggingMode(IntEnum):
    """
    :class:`~nodedge.graphics_view.DragMode` class.
    """

    NOOP = 1  #: Mode representing ready state
    EDGE_DRAG = 2  #: Mode representing when we drag edge state
    EDGE_CUT = 3  #: Mode representing when we draw a cutting edge


class EdgeDragging:
    """:class:`~nodedge.edge_dragging.EdgeDragging` class ."""

    # noinspection PyUnresolvedReferences
    def __init__(self, graphicsView: "GraphicsView") -> None:  # type: ignore
        self.graphicsView = graphicsView
        self.dragEdge: Optional[Edge] = None
        self.dragStartSocket: Optional[Socket] = None
        self.mode: EdgeDraggingMode = EdgeDraggingMode.NOOP

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)

    def update(self, item: Optional[QGraphicsItem]) -> None:
        """
        Update callback.

        :param item: selected item.
        :return: ``Optional[QGraphicsItem]``
        """
        if isinstance(item, GraphicsSocket):
            graphicsSocket: GraphicsSocket = item
            if self.mode == EdgeDraggingMode.NOOP:
                self.mode = EdgeDraggingMode.EDGE_DRAG
                self.__logger.debug(f"Drag mode: {self.mode}")
                self.startEdgeDragging(graphicsSocket)
                return
            elif self.mode == EdgeDraggingMode.EDGE_DRAG:
                ret = self.endEdgeDragging(graphicsSocket)
                if ret:
                    self.__logger.debug(f"Drag mode: {self.mode}")
                    return
        else:
            if self.mode == EdgeDraggingMode.EDGE_DRAG:
                self.mode = EdgeDraggingMode.NOOP
                self.endEdgeDragging(None)
                self.__logger.debug("End dragging edge early")

    def startEdgeDragging(self, graphicsSocket: GraphicsSocket):
        """
        Handle the start of dragging an :class:`~nodedge.edge.Edge` operation.

        :param graphicsSocket: The socket being connected to another one.
        :type graphicsSocket: :class:`~nodedge.graphics_socket.GraphicsSocket`
        """
        try:
            self.__logger.debug("Assign socket.")
            self.dragStartSocket = graphicsSocket.socket
            self.dragEdge = Edge(
                self.graphicsView.graphicsScene.scene,
                graphicsSocket.socket,
                edgeType=EdgeType.BEZIER,
            )
            self.dragEdge.graphicsEdge.makeUnselectable()

        except Exception as e:
            dumpException(e)

    def endEdgeDragging(self, graphicsSocket: Optional[GraphicsSocket]):
        """
        Handle the end of dragging an :class:`~nodedge.edge.Edge` operation.

        :param graphicsSocket: socket being connected
        :type graphicsSocket: :class:`~nodedge.graphics_socket.GraphicsSocket`
        :return: True is the operation is a success, false otherwise.
        :rtype: ``bool``
        """
        self.mode = EdgeDraggingMode.NOOP
        self.__logger.debug(f"Drag mode: {self.mode}")

        # noinspection PyBroadException
        try:
            if self.dragEdge is not None:
                # Don't notify sockets about removing drag_edge
                self.dragEdge.remove(silent=True)
        except Exception:
            self.__logger.warning("Impossible to remove dragEdge")
        self.dragEdge = None

        try:
            if self.dragStartSocket is not None:
                if not self.dragStartSocket.allowMultiEdges:
                    self.dragStartSocket.removeAllEdges()

            if graphicsSocket is None:
                return

            if not graphicsSocket.socket.allowMultiEdges:
                graphicsSocket.socket.removeAllEdges()

            newEdge = Edge(
                self.graphicsView.graphicsScene.scene,
                self.dragStartSocket,
                graphicsSocket.socket,
            )
            graphicsSocket.socket.addEdge(newEdge)
            self.__logger.debug(
                f"New edge created: {newEdge} connecting"
                f"\n|||| {newEdge.sourceSocket} to"
                f"\n |||| {newEdge.targetSocket}"
            )

            socket: Optional[Socket]
            for socket in [self.dragStartSocket, graphicsSocket.socket]:
                if socket is not None:
                    socket.node.onEdgeConnectionChanged(newEdge)

                    if socket.isInput:
                        socket.node.onInputChanged(socket)

            self.graphicsView.graphicsScene.scene.history.store(
                "Create a new edge by dragging"
            )
            self.__logger.debug("Socket assigned.")
            return True
        except Exception as e:
            dumpException(e)

        self.__logger.debug("Drag edge successful.")
        return False
