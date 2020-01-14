import logging

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from nodedge.blocks.block_config import *
from nodedge.edge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT
from nodedge.editor_widget import EditorWidget
from nodedge.node import Node
from nodedge.utils import dumpException


class MdiSubWindow(EditorWidget):
    def __init__(self):
        super().__init__()

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.__contextLogger = logging.getLogger(__file__ + "#Context")
        self.__contextLogger.setLevel(logging.DEBUG)

        self._closeEventListeners = []

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.scene.addHasBeenModifiedListener(self.updateTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)
        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self.updateTitle()

        self.initNewNodeActions()

    def initNewNodeActions(self):
        self.nodeActions = {}

        keys = list(BLOCKS.keys())
        keys.sort()

        for key in keys:
            node = BLOCKS[key]
            self.nodeActions[node.operationCode] = QAction(
                QIcon(node.icon), node.operationTitle
            )
            self.nodeActions[node.operationCode].setData(node.operationCode)

    def initNodesContextMenu(self):
        contextMenu = QMenu(self)
        keys = list(BLOCKS.keys())
        keys.sort()
        for key in keys:
            contextMenu.addAction(self.nodeActions[key])

        return contextMenu

    def getNodeClassFromData(self, data):
        if "operationCode" not in data:
            return Node
        return getClassFromOperationCode(data["operationCode"])

    def addCloseEventListener(self, callback):
        self._closeEventListeners.append(callback)

    def closeEvent(self, event: QCloseEvent) -> None:
        for callback in self._closeEventListeners:
            callback(self, event)
        self.__logger.debug("Everything done in after close event")

    def onDragEnter(self, event):
        if not event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            self.__logger.warning(
                f"Dragging denied: Wrong Mime format ({event.mimeData().formats()})"
            )
            event.setAccepted(False)
            return

        event.acceptProposedAction()

    def onDrop(self, event):
        if not event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.ignore()
            self.__logger.warning(
                f"Dropping denied: Wrong Mime format ({event.mimeData().formats()})"
            )
            return

        eventData = event.mimeData().data(LISTBOX_MIMETYPE)
        dataStream = QDataStream(eventData, QIODevice.ReadOnly)
        pixmap = QPixmap()
        dataStream >> pixmap
        operationCode = dataStream.readInt()
        text = dataStream.readQString()

        mousePos = event.pos()
        scenePos = self.scene.view.mapToScene(mousePos)

        self.__logger.debug(
            f"Received text ({text}) and code ({operationCode}) at pos ({scenePos})"
        )

        # FIXME: [WIP] Nodes should not be created this way.
        # node = Block(self.scene, text, operationCode)

        try:
            node = getClassFromOperationCode(operationCode)(self.scene)
            node.pos = (scenePos.x(), scenePos.y())
            self.scene.history.store(f"Created node {node.__class__.__name__}.")
        except Exception as e:
            dumpException(e)

        event.setDropAction(Qt.MoveAction)
        event.accept()

    def contextMenuEvent(self, event):
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
            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e:
            dumpException(e)

    def handleNodeContextMenu(self, event):
        contextMenu = QMenu()
        markDirtyAct = contextMenu.addAction("Mark dirty")
        markDescendantsDirtyAct = contextMenu.addAction("Mark descendants as dirty")
        markInvalidAct = contextMenu.addAction("Mark invalid")
        unmarkAct = contextMenu.addAction("Unmark invalid")
        evalAct = contextMenu.addAction("Eval")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

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

    def handleNewNodeContextMenu(self, event):
        contextMenu = self.initNodesContextMenu()
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

        if action is not None:
            newNode = getClassFromOperationCode(action.data())(self.scene)
            scenePos = self.scene.view.mapToScene(event.pos())
            newNode.setPos(scenePos.x(), scenePos.y())
            self.__contextLogger.debug(f"New node: {newNode}")

    def handleEdgeContextMenu(self, event):
        contextMenu = QMenu()
        bezierAct = contextMenu.addAction("Bezier Edge")
        directAct = contextMenu.addAction("Direct Edge")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.itemAt(event.pos())

        if hasattr(item, "edge"):
            selected = item.edge

        if selected and action == bezierAct:
            selected.edgeType = EDGE_TYPE_BEZIER
        if selected and action == directAct:
            selected.edgeType = EDGE_TYPE_DIRECT
