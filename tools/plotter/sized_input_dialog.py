# -*- coding: utf-8 -*-
"""
sized_input_dialog.py module containing :class:`~nodedge.sized_input_dialog.py.<ClassName>` class.
"""
from typing import Optional

from PySide2.QtCore import QSize
from PySide2.QtWidgets import QInputDialog


class SizedInputDialog(QInputDialog):
    def __init__(self, parent=None, sizeHint: Optional[QSize] = None):
        super().__init__(parent=parent)
        self.size = sizeHint

    def sizeHint(self) -> QSize:
        return self.size
