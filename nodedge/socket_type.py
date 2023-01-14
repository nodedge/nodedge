# -*- coding: utf-8 -*-
"""
<ModuleName> module containing :class:`~nodedge.<Name>.<ClassName>` class.
"""
from enum import Enum


class MyClass:
    """:class:`~nodedge.<ModuleName>.<ClassName>` class ."""


class SocketType(Enum):
    Any = 0
    Number = 1  # Int + Float + Double
    String = 2
    Integer = 3
    Float = 4
    Double = 5
    Boolean = 6
    Array = 7
    Object = 8
