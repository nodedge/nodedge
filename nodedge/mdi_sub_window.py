import logging

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from nodedge.editor_widget import EditorWidget
from nodedge.mdi_config import *
from nodedge.node import Node


class MdiSubWindow(EditorWidget):
    def __init__(self):
        super().__init__()

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

        self._closeEventListeners = []

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.scene.addHasBeenModifiedListener(self.updateTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)

        self.updateTitle()

    def addCloseEventListener(self, callback):
        self._closeEventListeners.append(callback)

    def closeEvent(self, event: QCloseEvent) -> None:
        for callback in self._closeEventListeners:
            callback(self, event)
        self.__logger.debug("Everything done in after close event")

    def onDragEnter(self, event):
        if not event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            self.__logger.warning(f"Dragging denied: Wrong Mime format ({event.mimeData().formats()})")
            event.setAccepted(False)
            return

        event.acceptProposedAction()

    def onDrop(self, event):
        if not event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.ignore()
            self.__logger.warning(f"Dropping denied: Wrong Mime format ({event.mimeData().formats()})")
            return

        eventData = event.mimeData().data(LISTBOX_MIMETYPE)
        dataStream = QDataStream(eventData, QIODevice.ReadOnly)
        pixmap = QPixmap()
        dataStream >> pixmap
        operationCode = dataStream.readInt()
        text = dataStream.readQString()

        mousePos = event.pos()
        scenePos = self.scene.graphicsScene.views()[0].mapToScene(mousePos)

        self.__logger.debug(f"Received text ({text}) and code ({operationCode}) at pos ({scenePos})")

        # FIXME: [WIP] Nodes should not be created this way.
        node = Node(self.scene, text, inputs=[1, 1], outputs=[2])
        node.setPos(scenePos.x(), scenePos.y())

        event.setDropAction(Qt.MoveAction)
        event.accept()



