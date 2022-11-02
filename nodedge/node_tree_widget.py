# -*- coding: utf-8 -*-
"""Node tree widget module containing
:class:`~nodedge.node_tree_widget.NodeTreeWidget` class. """

import logging
from typing import Optional

from PySide6.QtCore import (
    QByteArray,
    QDataStream,
    QIODevice,
    QMimeData,
    QPoint,
    QSize,
    Qt,
    Signal,
)
from PySide6.QtGui import QDrag, QIcon, QMouseEvent, QPixmap
from PySide6.QtWidgets import QAbstractItemView, QTreeWidget, QTreeWidgetItem, QWidget

from nodedge import DEBUG_ITEMS_PRESSED
from nodedge.blocks.block_config import *
from nodedge.utils import dumpException, widgetsAt

NODETREEWIDGET_MIMETYPE = "application/x-item"

COLUMNS = {
    "Name": 0,
}


class NodeTreeWidget(QTreeWidget):
    """
    Node tree widget class.

    The tree widget contains the declaration of all the available nodes.
    """

    itemsPressed = Signal(list)

    def __init__(self, parent: Optional[QWidget] = None):
        """

        :param parent: Qt widget parent
        :type parent: ``QWidget`` | ``None``
        """
        super().__init__(parent)

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)

        self.initUI()
        self.setSortingEnabled(True)
        self.setHeaderLabels(list(COLUMNS.keys()))

    # noinspection PyAttributeOutsideInit
    def initUI(self) -> None:
        """
        Set up this :class:`~nodedge.node_tree_widget.NodeTreeWidget` with its icon
        and :class:`~nodedge.node.Node`.
        """

        self.iconsSize: QSize = QSize(32, 32)
        self.setIconSize(self.iconsSize)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addNodes()

    def addNodes(self) -> None:
        """
        Add available :class:`~nodedge.node.Node` s in the tree widget.
        """
        # associateOperationCodeWithBlock(operationCode, blockClass)

        keys = list(BLOCKS.keys())
        keys.sort()

        for key in keys:
            node = getClassFromOperationCode(key)
            self.addNode(
                node.operationTitle, node.icon, node.operationCode, node.library
            )

    def addNode(
        self,
        name: str,
        iconPath: Optional[str] = None,
        operationCode: int = 0,
        libraryName: str = "",
    ):
        """
        Add a :class:`~nodedge.node.Node` in the tree widget.
        """

        item = QTreeWidgetItem()
        item.setText(0, name)
        pixmap = QPixmap(iconPath) if iconPath else "."
        # TODO: Investigate QIcon constructor
        item.setIcon(0, QIcon(pixmap))  # type: ignore
        item.setSizeHint(0, self.iconsSize)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        item.setData(0, Qt.UserRole, pixmap)
        item.setData(0, Qt.UserRole + 1, operationCode)

        libraryName = libraryName.capitalize()
        if libraryName == "":
            self.addTopLevelItem(item)
        else:
            items = self.findItems(libraryName, Qt.MatchExactly)
            if not items:
                libraryItem = QTreeWidgetItem()
                libraryItem.setText(0, libraryName)
                self.addTopLevelItem(libraryItem)
                libraryItem.addChild(item)
            else:
                items[0].addChild(item)

    def startDrag(self, *args, **kwargs) -> None:
        """
        Serialize data when a user start dragging a node from the tree, to be able to
        instantiate it later.
        """
        try:
            item = self.currentItem()
            operationCode = item.data(0, Qt.UserRole + 1)
            self.__logger.debug(
                f"Dragging text ({item.text(0)}) and code ({operationCode})"
            )
            pixmap = QPixmap(item.data(0, Qt.UserRole))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.WriteOnly)
            # left operand works fine with QDataStream
            dataStream << pixmap
            dataStream.writeInt32(operationCode)
            dataStream.writeQString(item.text(0))

            mimeData = QMimeData()
            mimeData.setData(NODETREEWIDGET_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)

        except Exception as e:
            dumpException(e)

    def mousePressEvent(self, e: QMouseEvent) -> None:
        """
        Handle Qt mouse press event.
        :param e: `QMouseEvent`
        :return: ``None``
        """
        if DEBUG_ITEMS_PRESSED:
            pos = e.globalPos()
            itemsPressed = [w.__class__.__name__ for w in widgetsAt(pos)]
            self.__logger.debug(itemsPressed)
            # noinspection PyUnresolvedReferences
            self.itemsPressed.emit(itemsPressed)
        super().mousePressEvent(e)
