# -*- coding: utf-8 -*-
"""A module containing base class for Node's content graphical representation. It also contains example of
overridden Text Widget which can pass to it's parent notification about currently being modified."""

from collections import OrderedDict
from typing import Optional, cast

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFocusEvent
from PyQt5.QtWidgets import QTextEdit, QVBoxLayout, QWidget

from nodedge.serializable import Serializable


class NodeContent(QWidget, Serializable):
    """Base class for representation of the Node's graphics content. This class also provides layout
    for other widgets inside of a :py:class:`~nodedge.node.Node`"""

    def __init__(self, node: "Node", parent: Optional[QWidget] = None):  # type: ignore
        """
        :param node: reference to the :py:class:`~nodedge.node.Node`
        :type node: :py:class:`~nodedge.node.Node`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:
            - **node** - reference to the :class:`~nodedge.node.Node`
            - **layout** - ``QLayout`` container
        """

        super().__init__(parent)
        self.node = node

        self.initUI()
        self.setAttribute(Qt.WA_TranslucentBackground)

    # noinspection PyAttributeOutsideInit
    def initUI(self):
        """Sets up layouts and widgets to be rendered in
        :py:class:`~nodedge.graphics_node.QDMGraphicsNode` class.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(AckTextEdit("X3"))

    def setEditingFlag(self, value: bool) -> None:
        """
        .. note::

            If you are handling keyPress events by default Qt Window's shortcuts and ``QActions``, you will not
            probably need to use this method

        Helper function which sets editingFlag inside :py:class:`~nodedge.graphics_view.QDMGraphicsView` class.

        This is a helper function to handle keys inside nodes with ``QLineEdits`` or ``QTextEdits`` (you can
        use overridden :py:class:`QDMTextEdit` class) and with QGraphicsView class method ``keyPressEvent``.

        :param value: new value for editing flag
        """

        self.node.scene.view.editingFlag = value

    def serialize(self) -> OrderedDict:
        """ Default serialization method.

        It needs to be overridden for each node implementation.


        :return OrderedDict: Serialized data as ordered dictionary
        """
        return OrderedDict([])

    def deserialize(
        self, data: dict, hashmap: Optional[dict] = None, restoreId: bool = False
    ) -> bool:
        """ Default deserialize method.

        It needs to be overridden for each node implementation.

        :param dict data: serialized data dictionary
        :param dict hashmap:
        :param bool restoreId: whether or not the id of the objects are restored
        :return bool: success status
        """
        if hashmap is None:
            hashmap = {}
        return True


class AckTextEdit(QTextEdit):
    """
    .. note::

        This class is example of ``QTextEdit`` modification to be able to handle `Delete` key with overridden
        Qt's ``keyPressEvent`` (when not using ``QActions`` in menu or toolbar)

    overridden ``QTextEdit`` which sends notification about being edited to parent's container :py:class:`QDMNodeContentWidget`
    """

    def focusInEvent(self, event: QFocusEvent) -> None:
        """Example of overridden focusInEvent to mark start of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """

        parent: NodeContent = cast(NodeContent, super().parentWidget())
        parent.setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """Example of overridden focusOutEvent to mark end of editing

        :param event: Qt's focus event
        :type event: QFocusEvent
        """

        parent: NodeContent = cast(NodeContent, super().parentWidget())
        parent.setEditingFlag(False)
        super().focusOutEvent(event)
