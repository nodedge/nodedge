# -*- coding: utf-8 -*-
"""
graphics_element.py module containing
:class:`~nodedge.graphics_element.GraphicsElement` class.
"""
from typing import Optional

from PySide6.QtWidgets import QGraphicsItem


class GraphicsElement(QGraphicsItem):
    def __init__(
        self, element: "Element", parent: Optional[QGraphicsItem] = None  # type: ignore
    ) -> None:
        super().__init__(parent)

        self.element = element
