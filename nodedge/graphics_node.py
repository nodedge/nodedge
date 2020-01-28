import logging

from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFont, QPainterPath, QPen
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsProxyWidget, QGraphicsTextItem


class GraphicsNode(QGraphicsItem):
    def __init__(self, node, parent=None):
        super().__init__(parent)
        self.node = node
        self.content = self.node.content

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.initUI()
        self._wasMoved = False
        self._lastSelectedState = False

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.titleItem.setPlainText(self._title)

    @property
    def selectedState(self):
        return self._lastSelectedState

    @selectedState.setter
    def selectedState(self, value):
        self._lastSelectedState = value

    def initUI(self):
        self.initSizes()
        self.initStyle()
        self.initTitle()
        self.initContent()

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    # noinspection PyAttributeOutsideInit
    def initStyle(self):
        self._titleColor: int = Qt.white
        self._titleFont: QFont = QFont("Ubuntu", 10)
        self._penDefault: QPen = QPen(QColor("#7F000000"))
        self._penSelected: QPen = QPen(QColor("#FFFFA637"))
        self._brushTitle: QBrush = QBrush(QColor("#FF313131"))
        self._brushBackground: QBrush = QBrush(QColor("#E3212121"))

    # noinspection PyAttributeOutsideInit
    def initSizes(self):
        self.width: int = 180
        self.height: int = 240
        self.edgeRoundness: float = 5.0
        self.edgePadding: float = 10.0
        self.titleHeight: float = 24.0
        self.titleHorizontalPadding: float = 4.0
        self.titleVerticalPadding: float = 4.0

    # noinspection PyAttributeOutsideInit
    def initTitle(self):
        self.titleItem = QGraphicsTextItem(self)
        self.titleItem.setDefaultTextColor(self._titleColor)
        self.titleItem.setFont(self._titleFont)
        self.titleItem.setPos(self.titleHorizontalPadding, 0)
        self.titleItem.setTextWidth(self.width - 2 * self.titleHorizontalPadding)
        self.titleItem.node = self.node

        self.title = self.node.title

    # noinspection PyAttributeOutsideInit
    def initContent(self):
        self.graphicsContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(
            self.edgePadding,
            self.titleHeight + self.edgePadding,
            self.width - 2 * self.edgePadding,
            self.height - 2 * self.edgePadding - self.titleHeight,
        )
        self.graphicsContent.setWidget(self.content)

    def boundingRect(self):
        return QRectF(0, 0, self.width, self.height).normalized()

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):

        # title
        pathTitle = QPainterPath()
        pathTitle.setFillRule(Qt.WindingFill)
        pathTitle.addRoundedRect(
            0, 0, self.width, self.titleHeight, self.edgeRoundness, self.edgeRoundness
        )
        maxTopRect = max(self.titleHeight - self.edgeRoundness, self.titleHeight / 2.0)
        maxHeightRect = min(self.edgeRoundness, self.titleHeight / 2.0)
        pathTitle.addRect(0, maxTopRect, self.edgeRoundness, maxHeightRect)
        pathTitle.addRect(
            self.width - self.edgeRoundness,
            maxTopRect,
            self.edgeRoundness,
            maxHeightRect,
        )

        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brushTitle)
        painter.drawPath(pathTitle.simplified())

        # content
        pathContent = QPainterPath()
        pathContent.setFillRule(Qt.WindingFill)
        pathContent.addRoundedRect(
            0,
            self.titleHeight,
            self.width,
            self.height - self.titleHeight,
            self.edgeRoundness,
            self.edgeRoundness,
        )
        maxHeightRect = min(self.edgeRoundness, self.height / 2)
        pathContent.addRect(0, self.titleHeight, self.edgeRoundness, maxHeightRect)
        pathContent.addRect(
            self.width - self.edgeRoundness,
            self.titleHeight,
            self.edgeRoundness,
            maxHeightRect,
        )
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brushBackground)
        painter.drawPath(pathContent.simplified())

        # outline
        pathOutline = QPainterPath()
        pathOutline.addRoundedRect(
            0, 0, self.width, self.height, self.edgeRoundness, self.edgeRoundness
        )
        painter.setPen(self._penDefault if not self.isSelected() else self._penSelected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(pathOutline.simplified())

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        # TODO: Optimize this condition. Just update the selected blocks.
        for node in self.scene().scene.nodes:
            if node.graphicsNode.isSelected():
                node.updateConnectedEdges()

        self._wasMoved = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        # Handle when node moved
        if self._wasMoved:
            self._wasMoved = False
            self.node.scene.history.store("Move a node")

            self.node.scene.resetLastSelectedStates()
            self._lastSelectedState = True

            # Store the last selected, because moving does also select the blocks.
            self.node.scene.lastSelectedItems = self.node.scene.selectedItems

            # Skip storing selection as it has just been done.
            return

        # Handle when node was clicked on
        isSelected = self.isSelected()
        if (
            self._lastSelectedState != isSelected
            or self.node.scene.lastSelectedItems != self.node.scene.selectedItems
        ):
            self.node.scene.resetLastSelectedStates()
            self._lastSelectedState = isSelected
            self.onSelected()

    def onSelected(self):
        self.__logger.debug("")
        self.node.scene.graphicsScene.itemSelected.emit()
