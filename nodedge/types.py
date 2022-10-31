# -*- coding: utf-8 -*-
"""
types.py module containing :class:`~nodedge.types.py.<ClassName>` class.
"""
from typing import List, Tuple, TypeVar

from PySide6.QtCore import QPoint, QPointF

Pos = TypeVar("Pos", List, Tuple, QPoint, QPointF)
