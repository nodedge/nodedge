import logging
from typing import Optional

from PyQt5.QtCore import (
    QByteArray,
    QDataStream,
    QIODevice,
    QMimeData,
    QPoint,
    QSize,
    Qt,
)
from PyQt5.QtGui import QDrag, QIcon, QPixmap
from PyQt5.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem

from nodedge.blocks.block_config import *
from nodedge.utils import dumpException


class DragListbox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)

        self.initUI()

    # noinspection PyAttributeOutsideInit
    def initUI(self):
        self.iconSize: QSize = QSize(32, 32)
        self.setIconSize(self.iconSize)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addNodes()

    def addNodes(self):
        # associateOperationCodeWithBlock(operationCode, blockClass)

        keys = list(BLOCKS.keys())
        keys.sort()

        for key in keys:
            node = getClassFromOperationCode(key)
            self.addNode(node.operationTitle, node.icon, node.operationCode)

    def addNode(self, name, iconPath: Optional[str] = None, operationCode: int = 0):
        item = QListWidgetItem(name, self)
        pixmap = QPixmap(iconPath) if iconPath else "."
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(self.iconSize)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)  # type: ignore

        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, operationCode)

    def startDrag(self, *args, **kvargs) -> None:
        try:
            item = self.currentItem()
            operationCode = item.data(Qt.UserRole + 1)
            self.__logger.debug(
                f"Dragging text ({item.text()}) and code ({operationCode})"
            )
            pixmap = QPixmap(item.data(Qt.UserRole))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            dataStream << pixmap  # type: ignore # left operand works fine with QDataStream
            dataStream.writeInt(operationCode)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            dumpException(e)
