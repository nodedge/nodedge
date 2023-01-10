# -*- coding: utf-8 -*-
"""Graphics node title item module containing
:class:`~nodedge.graphics_node_title_label.GraphicsNodeTitleLabel` class. """
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QLabel, QWidget


class GraphicsNodeTitleLabel(QLabel):
    """
    :class:`~nodedge.graphics_node_title_label.GraphicsNodeTitleLabel` class.
    """

    def __init__(self, text, graphicsNodeWidget: QWidget) -> None:
        super().__init__(text, graphicsNodeWidget)
        self.graphicsNodeWidget = graphicsNodeWidget

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        self.setFocus()
        super().mousePressEvent(ev)


class GraphicsNodeTypeLabel(QLabel):
    """
    :class:`~nodedge.graphics_node_title_label.GraphicsNodeTypeLabel` class.
    """

    def __init__(self, text, graphicsNodeWidget: QWidget) -> None:
        super().__init__(text, graphicsNodeWidget)
        self.graphicsNodeWidget = graphicsNodeWidget
