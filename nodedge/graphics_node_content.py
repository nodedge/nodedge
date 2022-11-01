# -*- coding: utf-8 -*-
"""Graphics node content module containing the
:class:`~nodedge.graphics_node_content.GraphicsNodeContent` class. """

from collections import OrderedDict
from typing import Optional, cast

from PySide6.QtGui import QFocusEvent
from PySide6.QtWidgets import QGraphicsProxyWidget, QTextEdit, QVBoxLayout, QWidget

from nodedge.serializable import Serializable


class GraphicsNodeContent(QWidget, Serializable):
    """
    :class:`~nodedge.graphics_node_content.GraphicsNodeContent` class.

    Base class for representation of the Node's graphics content. This class also
    provides layout for other widgets inside of a :py:class:`~nodedge.node.Node`.
    """

    def __init__(
        self, node: "Node", parent: Optional[QWidget] = None  # type: ignore
    ) -> None:
        """
        :param node: reference to the :py:class:`~nodedge.node.Node`
        :type node: :py:class:`~nodedge.node.Node`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:
            - **node** - reference to the :class:`~nodedge.node.Node`
            - **layout** - ``QLayout`` container
        """

        QWidget.__init__(self, parent)
        self.node: "Node" = node  # type: ignore
        self.initUI()

    # noinspection PyAttributeOutsideInit
    def initUI(self):
        """
        Sets up layouts and widgets to be rendered in
        :py:class:`~nodedge.graphics_node.QDMGraphicsNode` class.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.layout.addWidget(TextEdit("N"))

    def setEditingFlag(self, value: bool) -> None:
        """
        .. note::

            If you are handling keyPress events by default Qt Window's shortcuts and
            ``QActions``, you will not probably need to use this method

        Helper function which sets editingFlag inside
        :py:class:`~nodedge.graphics_view.GraphicsView` class.

        This is a helper function to handle keys inside nodes with ``QLineEdits`` or
        ``QTextEdits`` (you can use overridden :py:class:`TextEdit` class) and with
        QGraphicsView class method ``keyPressEvent``.

        :param value: new value for editing flag
        :type value: ``bool``
        """

        self.node.scene.graphicsView.editingFlag = value

    def serialize(self) -> OrderedDict:
        """Default serialization method.

        It needs to be overridden for each node implementation.

        :return OrderedDict: Serialized data as ordered dictionary
        """
        return OrderedDict([])

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = False,
        *args,
        **kwargs
    ) -> bool:
        """Default deserialize method.

        It needs to be overridden for each node implementation.

        :param dict data: serialized data dictionary
        :param dict hashmap:
        :param bool restoreId: whether or not the id of the objects are restored
        :return bool: success status
        """
        if hashmap is None:
            hashmap = {}
            hashmap.clear()
        return True


class TextEdit(QTextEdit):
    """
    .. note::

        This class is example of ``QTextEdit`` modification to be able to handle
        `Delete` key with overridden Qt ``keyPressEvent`` (when not using
        ``QActions`` in menu or toolbar)

    overridden ``QTextEdit`` which sends notification about being edited to parent's
    container :py:class:`GraphicsNodeContent`
    """

    def focusInEvent(self, event: QFocusEvent) -> None:
        """
        Example of overridden focusInEvent to mark start of editing.

        :param event: Qt focus event
        :type event: QFocusEvent
        """

        parent: GraphicsNodeContent = cast(GraphicsNodeContent, super().parentWidget())
        parent.setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event: QFocusEvent) -> None:
        """
        Example of overridden focusOutEvent to mark end of editing

        :param event: Qt focus event
        :type event: QFocusEvent
        """

        parent: GraphicsNodeContent = cast(GraphicsNodeContent, super().parentWidget())
        parent.setEditingFlag(False)
        super().focusOutEvent(event)


class GraphicsNodeContentProxy(QGraphicsProxyWidget):
    """
    :class:`~nodedge.graphics_node_content.GraphicsNodeContentProxy` class.

    It is a ``QGraphicsProxyWidget`` around the
    :class:`~nodedge.graphics_node_content.GraphicsNodeContent`.
    """

    def __init__(self, graphicsNodeParent: "GraphicsNode") -> None:  # type: ignore
        super().__init__(graphicsNodeParent)
        self.setWidget(graphicsNodeParent.content)
