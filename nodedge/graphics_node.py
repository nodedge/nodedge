from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class GraphicsNode(QGraphicsItem):
    def __init__(self, node, parent=None):
        super().__init__(parent)

        self.node = node
        self.content = self.node.content
        self.wasMoved = False

        self._title_color = Qt.white
        self._title_font = QFont("Ubuntu", 10)

        self.width = 180
        self.height = 240
        self.edge_size = 10.
        self.titleHeight = 24.
        self._padding = 4.

        # Init title
        self.initTitle()
        self.title = self.node.title

        # Init socket
        self.initSocket()

        # Init content
        self.initContent()

        self._pen_default = QPen(QColor("#7F000000"))
        self._pen_selected = QPen(QColor("#FFFFA637"))
        self._brush_title = QBrush(QColor("#FF313131"))
        self._brush_background = QBrush(QColor("#E3212121"))

        self.initUI()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        #TODO: Optimize this condition. Just update the selected nodes.
        for node in self.scene().scene.nodes:
            if node.graphicsNode.isSelected():
                node.updateConnectedEdges()

        self.wasMoved = True

    def mouseReleaseEvent(self, event):
        if self.wasMoved:
            self.wasMoved = False
            self.node.scene.history.store("Move a node")
        super().mouseReleaseEvent(event)

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.title_item.setPlainText(self._title)

    def boundingRect(self):
        return QRectF(0, 0,
                      self.width,
                      self.height).normalized()

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def initTitle(self):
        self.title_item = QGraphicsTextItem(self)
        self.title_item.node = self.node
        self.title_item.setDefaultTextColor(self._title_color)
        self.title_item.setFont(self._title_font)
        self.title_item.setPos(self._padding, 0)
        self.title_item.setTextWidth(self.width - 2*self._padding)

    def initContent(self):
        self.graphicsContent = QGraphicsProxyWidget(self)
        self.content.setGeometry(self.edge_size, self.titleHeight + self.edge_size,
                                 self.width - 2 * self.edge_size, self.height - 2 * self.edge_size - self.titleHeight)
        self.graphicsContent.setWidget(self.content)

    def initSocket(self):
        pass

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):

        # title
        path_title = QPainterPath()
        path_title.setFillRule(Qt.WindingFill)
        path_title.addRoundedRect(0, 0,
                                  self.width, self.titleHeight,
                                  self.edge_size, self.edge_size)
        path_title.addRect(0, self.titleHeight - self.edge_size, self.edge_size, self.edge_size)
        path_title.addRect(self.width - self.edge_size, self.titleHeight - self.edge_size, self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_title)
        painter.drawPath(path_title.simplified())

        # content
        path_content = QPainterPath()
        path_content.setFillRule(Qt.WindingFill)
        path_content.addRoundedRect(0, self.titleHeight,
                                    self.width, self.height - self.titleHeight,
                                    self.edge_size, self.edge_size)
        path_content.addRect(0, self.titleHeight,
                             self.edge_size, self.edge_size)
        path_content.addRect(self.width - self.edge_size, self.titleHeight,
                             self.edge_size, self.edge_size)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._brush_background)
        painter.drawPath(path_content.simplified())



        # outline
        path_outline = QPainterPath()
        path_outline.addRoundedRect(0, 0, self.width, self.height, self.edge_size, self.edge_size)
        painter.setPen(self._pen_default if not self.isSelected() else self._pen_selected)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path_outline.simplified())