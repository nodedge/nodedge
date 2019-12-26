import logging
import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from nodedge.utils import dumpException
from nodedge.blocks.block_config import *


class DragListbox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)

        self.initUI()

    def initUI(self):
        self.iconSize = QSize(32, 32)
        self.setIconSize(self.iconSize)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addNodes()

    def addNodes(self):
        nodesIconPath = f"{os.path.dirname(__file__)}/resources/node_icons"

        self.addNode("Input", f"{nodesIconPath}/in.png", OP_NODE_IN)
        self.addNode("Ouput", f"{nodesIconPath}/out.png", OP_NODE_OUT)
        self.addNode("Add", f"{nodesIconPath}/add.png", OP_NODE_ADD)
        self.addNode("Substract", f"{nodesIconPath}/subtract.png", OP_NODE_SUBTRACT)
        self.addNode("Multiply", f"{nodesIconPath}/multiply.png", OP_NODE_MULTIPLY)
        self.addNode("Divide", f"{nodesIconPath}/divide.png", OP_NODE_DIVIDE)

    def addNode(self, name, iconPath=None, operationCode=0):
        item = QListWidgetItem(name, self)
        pixmap = QPixmap(iconPath) if iconPath else "."
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(self.iconSize)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole+1, operationCode)

    def startDrag(self, *args, **kvargs) -> None:
        try:
            item = self.currentItem()
            operationCode = item.data(Qt.UserRole+1)
            self.__logger.debug(f"Dragging text ({item.text()}) and code ({operationCode})")
            pixmap = QPixmap(item.data(Qt.UserRole))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap
            dataStream.writeInt(operationCode)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width()/2, pixmap.height()/2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            dumpException(e)
