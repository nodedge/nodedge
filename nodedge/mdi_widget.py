# -*- coding: utf-8 -*-
"""
Mdi widget module containing :class:`~nodedge.mdi_widget.MdiWidget` class.
"""
import logging
from typing import Callable, List, Optional

from PySide6.QtCore import QDataStream, QIODevice, Qt
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QContextMenuEvent,
    QDragEnterEvent,
    QDropEvent,
    QIcon,
    QMouseEvent,
    QPixmap,
)
from PySide6.QtWidgets import QGraphicsProxyWidget, QGraphicsTextItem, QMenu

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import BLOCKS, getClassFromOperationCode
from nodedge.connector import Socket
from nodedge.edge import EdgeType
from nodedge.editor_widget import EditorWidget
from nodedge.graphics_view import EdgeDraggingMode
from nodedge.node import Node
from nodedge.node_tree_widget import NODETREEWIDGET_MIMETYPE
from nodedge.utils import dumpException


class MdiWidget(EditorWidget):
    """
    :class:`~nodedge.mdi_widget.MdiWidget` class.

    The mdi widget represents a sub-window of the
    :class:`~nodedge.mdi_window.MdiWindow`.
    """

    def __init__(self):
        super().__init__()

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.__contextLogger = logging.getLogger(__file__ + "#Context")
        self.__contextLogger.setLevel(logging.INFO)

        self._closeEventListeners: List[Callable] = []

        # self.setAttribute(Qt.WA_DeleteOnClose)

        self.scene.addHasBeenModifiedListener(self.updateTitle)
        # self.scene.history.addHistoryStoredListener(self.onHistoryStored)
        self.scene.history.addHistoryRestoredListener(self.evalNodes)
        self.scene.history.addHistoryRestoredListener(self.updateTitle)
        self.scene.addDragEnterListener(self.onNodeDragEnter)
        self.scene.addDropListener(self.onNodeDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self.updateTitle()

        self.initNewNodeActions()

    # noinspection PyAttributeOutsideInit
    def initNewNodeActions(self):
        """
        Add all available blocks in the
        :class:`~nodedge.node_list_widget.NodeListWidget`.
        """
        self.nodeActions = {}

        keys = list(BLOCKS.keys())
        keys.sort()

        for key in keys:
            node: Block = BLOCKS[key]
            self.nodeActions[node.operationCode] = QAction(
                QIcon(node.icon), node.operationTitle
            )
            self.nodeActions[node.operationCode].setData(node.operationCode)

    def initNodesContextMenu(self):
        """
        Create a context menu containing all the nodes available, so that the user
        can quickly create a new block by right clicking on the
        :class:`~nodedge.scene.Scene`.
        """
        contextMenu = QMenu(self)
        keys = list(BLOCKS.keys())
        keys.sort()
        for key in keys:
            contextMenu.addAction(self.nodeActions[key])

        return contextMenu

    @staticmethod
    def getNodeClassFromData(data):
        """Get the node class associated with operation present in data.

        :param data: serialized :class:`~nodedge.node.Node` containing the operation
            code
        :type: ``dict``
        :return: class of the node associated with the operation code in data,
            node class in case of failure.
        :rtype: Node class
        """
        if "operationCode" not in data:
            return Node
        return getClassFromOperationCode(data["operationCode"])

    def addCloseEventListener(
        self, callback: Callable[[EditorWidget, QCloseEvent], None]
    ):
        """
        Register callback for `Has Been Modified` event

        :param callback: callback function
        :type callback: Callable[[], None]
        """
        self._closeEventListeners.append(callback)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Handle Qt close event.

        Make sure changes have been saved before closing the widget.

        :param event: Qt close event, the user may have clicked on the close button,
            or pressed CTRL+W
        :type event: ``QCloseEvent.py``
        """
        for callback in self._closeEventListeners:
            callback(self, event)
        self.__logger.debug("Everything done in after close event")

    def onNodeDragEnter(self, event: QDragEnterEvent):
        """
        Handle node drag enter event.

        When a node is dragged from the
        :class:`~nodedge.node_list_widget.NodeListWidget`, its logo is displayed
        above the scene, near the location of the mouse.

        :param event: the Qt drag event event, containing the mime data of the node
            being dragged
        :return: QDragEnterEvent
        """
        if not event.mimeData().hasFormat(NODETREEWIDGET_MIMETYPE):
            self.__logger.warning(
                f"Dragging denied: Wrong Mime format ({event.mimeData().formats()})"
            )
            event.setAccepted(False)
            return

        event.acceptProposedAction()

    def onNodeDrop(self, event: QDropEvent):
        """
        Handle node drop event.

        When the node is dropped, an instance of it is created near at the mouse
        location, displayed by its :class:`~nodedge.graphics_node.GraphicsNode`.

        :param event: the Qt drop event, containing the mime data of the node being
            dropped.
        :type event: QDropEvent.py
        """
        if not event.mimeData().hasFormat(NODETREEWIDGET_MIMETYPE):
            event.ignore()
            self.__logger.warning(
                f"Dropping denied: Wrong Mime format ({event.mimeData().formats()})"
            )
            return

        eventData = event.mimeData().data(NODETREEWIDGET_MIMETYPE)
        dataStream = QDataStream(eventData, QIODevice.ReadOnly)
        pixmap: QPixmap = QPixmap()

        dataStream >> pixmap
        operationCode = dataStream.readInt32()
        text = dataStream.readQString()

        mousePos = event.pos()
        scenePos = self.scene.graphicsView.mapToScene(mousePos)

        self.__logger.debug(
            f"Received text ({text}) and code ({operationCode}) at pos ({scenePos})"
        )

        # FIXME: [WIP] Nodes should not be created this way.
        # node = Block(self.scene, text, operationCode)

        try:
            node = getClassFromOperationCode(operationCode)(self.scene)
            node.pos = (scenePos.x(), scenePos.y())
            self.scene.history.store(f"Create {node.__class__.__name__}")
        except Exception as e:
            dumpException(e)

        event.setDropAction(Qt.MoveAction)
        event.accept()

    def contextMenuEvent(self, event: QContextMenuEvent):
        """
        Handle Qt context menu event.


        :param event: the Qt context menu event, happening when the user right
            clicks on the :class:`~nodedge.graphics_scene.GraphicsScene`
        :type event: ``QContextMenuEvent.py``
        """
        try:
            item = self.scene.itemAt(event.pos())
            self.__contextLogger.debug(f"{item}")

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, "node") or hasattr(item, "socket"):
                self.handleNodeContextMenu(event)
            elif hasattr(item, "edge"):
                self.handleEdgeContextMenu(event)
            # elif item is None:
            elif isinstance(item, QGraphicsTextItem):
                self.__contextLogger.debug("Right click on a comment.")
            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e:
            dumpException(e)

    def handleNodeContextMenu(self, event: QContextMenuEvent):
        """
        Handle Qt context menu event when the user has clicked on a node.

        :param event: Qt context menu event, happening when the users
        :return: ``QContextMenuEvent``
        """
        contextMenu = QMenu()
        markDirtyAct = contextMenu.addAction("Mark dirty")
        markDescendantsDirtyAct = contextMenu.addAction("Mark descendants as dirty")
        markInvalidAct = contextMenu.addAction("Mark invalid")
        unmarkAct = contextMenu.addAction("Unmark invalid")
        evalAct = contextMenu.addAction("Eval")
        action = QMenu.exec_(self.mapToGlobal(event.pos()))  # type: ignore

        selected = None
        item = self.scene.itemAt(event.pos())

        if type(item) == QGraphicsProxyWidget:
            item = item.widget()

        if hasattr(item, "node"):
            selected = item.node
        elif hasattr(item, "socket"):
            selected = item.socket.node

        self.__contextLogger.debug(f"Node {selected} is selected")

        if selected is not None:
            if action == markDirtyAct:
                selected.isDirty = True
            elif action == markDescendantsDirtyAct:
                selected.markDescendantsDirty()
            elif action == unmarkAct:
                selected.isInvalid = False
            elif action == markInvalidAct:
                selected.isInvalid = True
            elif action == evalAct:
                val = selected.eval()
                self.__contextLogger.debug(f"Evaluated value: {val}")

            # Manually trigger paint method.
            selected.graphicsNode.update()

    # helper functions
    @staticmethod
    def determineTargetSocketOfNode(
        wasDraggedFlag: bool, newNode: Node
    ) -> Optional[Socket]:
        targetSocket = None
        if wasDraggedFlag:
            if len(newNode.inputSockets) > 0:
                targetSocket = newNode.inputSockets[0]
        else:
            if len(newNode.outputSockets) > 0:
                targetSocket = newNode.outputSockets[0]
        return targetSocket

    def finishNewNodeState(self, newNode):
        self.scene.doDeselectItems()
        newNode.isSelected = True

    def handleNewNodeContextMenu(self, event):
        """
        Handle context menu event when the users has right clicked on an empty space.

        Show all available nodes available in a list context menu, so that the users
        can quickly create a new one.

        :param event: the Qt context menu event, happening when the user right
            clicks on the :class:`~nodedge.graphics_scene.GraphicsScene`
        :type event: ``QContextMenuEvent.py``
        """
        contextMenu = self.initNodesContextMenu()
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            newNode = getClassFromOperationCode(action.data())(self.scene)
            scenePos = self.scene.graphicsView.mapToScene(event.pos())
            newNode.pos = scenePos
            self.__contextLogger.debug(f"New node: {newNode}")

            if self.scene.graphicsView.edgeDragging.mode == EdgeDraggingMode.EDGE_DRAG:
                self.scene.graphicsView.edgeDragging.endEdgeDragging(
                    newNode.inputSockets[0].graphicsSocket
                )

                # newNode.isSelected = True

                targetSocket: Optional[Socket] = MdiWidget.determineTargetSocketOfNode(
                    self.scene.graphicsView.edgeDragging.dragStartSocket.isOutput,
                    newNode,
                )

                if targetSocket is not None:
                    self.scene.graphicsView.edgeDragging.endEdgeDragging(
                        targetSocket.graphicsSocket
                    )
                    self.finishNewNodeState(newNode)

                # newNode.inputSockets[0].edges[-1].isSelected = True

            else:
                self.scene.history.store(
                    f"Created new node: {newNode.__class__.__name__}"
                )

    def handleEdgeContextMenu(self, event):
        """
        Handle Qt context menu when the user has right clicked on an
        :class:`~nodedge.graphics_edge.GraphicsEdge`

        :param event: the Qt context menu event, happening when the user right clicks
            on the :class:`~nodedge.graphics_scene.GraphicsScene`
        :type event: ``QContextMenuEvent``
        """
        contextMenu = QMenu()
        bezierAct = contextMenu.addAction("Bezier Edge")
        directAct = contextMenu.addAction("Direct Edge")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.itemAt(event.pos())

        if hasattr(item, "edge"):
            selected = item.edge

        if selected and action == bezierAct:
            selected.edgeType = EdgeType.BEZIER
        if selected and action == directAct:
            selected.edgeType = EdgeType.STRAIGHT

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Handle Qt mouse release event.

        :param event: Qt mouse release event
        :return: ``QMouseEvent``
        """
        super().mouseReleaseEvent(event)
