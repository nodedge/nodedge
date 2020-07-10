# -*- coding: utf-8 -*-
"""Graphics node title item module containing
:class:`~nodedge.graphics_node_title_item.GraphicsNodeTitleItem` class. """

from PySide2.QtWidgets import QGraphicsTextItem


class GraphicsNodeTitleItem(QGraphicsTextItem):
    """
    :class:`~nodedge.graphics_node_title_item.GraphicsNodeTitleItem` class.
    """

    def __init__(self, graphicsNodeParent: "GraphicsNode") -> None:  # type: ignore
        super().__init__(graphicsNodeParent)
        self.graphicsNode = graphicsNodeParent
