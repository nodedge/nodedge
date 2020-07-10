# -*- coding: utf-8 -*-
"""Node list widget module containing
:class:`~nodedge.node_list_widget.NodeListWidget` class. """

import logging
from typing import Optional

from PySide2.QtCore import (
    QByteArray,
    QDataStream,
    QIODevice,
    QMimeData,
    QPoint,
    QSize,
    Qt,
    Signal,
)
from PySide2.QtGui import QDrag, QIcon, QMouseEvent, QPixmap
from PySide2.QtWidgets import QAbstractItemView, QListWidget, QListWidgetItem, QWidget

from nodedge import DEBUG_ITEMS_PRESSED
from nodedge.blocks.block_config import *
from nodedge.utils import dumpException, widgetsAt


class NodeListWidget(QListWidget):
    """
    Node list widget class.

    The list widget contains the declaration of all the available nodes.
    """

    itemsPressed = Signal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        """

        :param parent: Qt's widget parent
        :type parent: ``QWidget`` | ``None``
        """
        super().__init__(parent)

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)

        self.initUI()

    # noinspection PyAttributeOutsideInit
    def initUI(self) -> None:
        """
        Set up this :class:`~nodedge.node_list_widget.NodeListWidget` with its icon
        and :class:`~nodedge.node.Node`.
        """

        self.iconsSize: QSize = QSize(32, 32)
        self.setIconSize(self.iconsSize)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addNodes()

    def addNodes(self) -> None:
        """
        Add available :class:`~nodedge.node.Node` s in the list widget.
        """
        # associateOperationCodeWithBlock(operationCode, blockClass)

        keys = list(BLOCKS.keys())
        keys.sort()

        for key in keys:
            node = getClassFromOperationCode(key)
            self.addNode(node.operationTitle, node.icon, node.operationCode)

    def addNode(self, name, iconPath: Optional[str] = None, operationCode: int = 0):
        """
        Add a :class:`~nodedge.node.Node` in the list widget.
        """
        item = QListWidgetItem(name, self)
        pixmap = QPixmap(iconPath) if iconPath else "."
        # TODO: Investigate QIcon constructor
        item.setIcon(QIcon(pixmap))  # type: ignore
        item.setSizeHint(self.iconsSize)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole + 1, operationCode)

    def startDrag(self, *args, **kwargs) -> None:
        """
        Serialize data when a user start dragging a node from the list, to be able to
        instantiate it later.
        """
        try:
            item = self.currentItem()
            operationCode = item.data(Qt.UserRole + 1)
            self.__logger.debug(
                f"Dragging text ({item.text()}) and code ({operationCode})"
            )
            pixmap = QPixmap(item.data(Qt.UserRole))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            # left operand works fine with QDataStream
            dataStream << pixmap
            dataStream.writeInt32(operationCode)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(NODELISTWIDGET_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            dumpException(e)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if DEBUG_ITEMS_PRESSED:
            pos = e.globalPos()
            itemsPressed = [w.__class__.__name__ for w in widgetsAt(pos)]
            self.__logger.debug(itemsPressed)
            # noinspection PyUnresolvedReferences
            self.itemsPressed.emit(itemsPressed)  # type: ignore
        super().mousePressEvent(e)
