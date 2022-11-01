# -*- coding: utf-8 -*-
"""
Editor widget module containing :class:`~nodedge.editor_widget.EditorWidget` class.
"""

import logging
import os
from typing import List, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QMouseEvent, QPen
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

from nodedge.blocks.block import Block
from nodedge.edge import Edge, EdgeType
from nodedge.graphics_view import GraphicsView
from nodedge.node import Node
from nodedge.scene import InvalidFile, Scene
from nodedge.socket_type import SocketType
from nodedge.utils import dumpException


class EditorWidget(QWidget):
    """:class:`~nodedge.editor_widget.EditorWidget` class"""

    SceneClass = Scene
    GraphicsViewClass = GraphicsView
    """
    :class:`~nodedge.editor_widget.EditorWidget` class

    The editor widget is the main widget of the ``QMainWindow``.
    """

    def __init__(self, parent=None):
        """
        Default constructor.

        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance Attributes:

        - **filename** - currently graph's filename or ``None``
        """
        super().__init__(parent)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.filename: str = ""

        self.initUI()

    # noinspection PyAttributeOutsideInit
    def initUI(self):
        """
        Set up this :class:`~nodedge.editor_widget.EditorWidget` with its layout,
        :class:`~nodedge.scene.Scene` and :class:`~nodedge.graphics_view.GraphicsView`.
        """

        self.layout: QVBoxLayout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.layout)
        self.scene: Scene = self.__class__.SceneClass()
        self.graphicsView: GraphicsView = self.__class__.GraphicsViewClass(
            self.scene.graphicsScene, self
        )
        self.layout.addWidget(self.graphicsView)

    @property
    def hasName(self) -> bool:
        """
        :getter: Return if a file has been loaded in this
            :class:`~nodedge.editor_widget.EditorWidget` or not.

        :rtype: ``bool``
        """
        return self.filename != ""

    @property
    def shortName(self) -> str:
        """
        :getter: Return the short name of this
            :class:`~nodedge.editor_widget.EditorWidget`.

        :rtype: ``str``
        """
        return os.path.basename(self.filename)

    @property
    def userFriendlyFilename(self) -> str:
        """
        :getter: Return the user friendly filename.

        .. note::

            This name is displayed as window title.

        :rtype: ``str``
        """
        name = os.path.basename(self.filename) if self.hasName else "New graph"

        return name + ("*" if self.isModified else "")

    @property
    def isModified(self) -> bool:
        """
        :getter: Has current :class:`~nodedge.scene.Scene` been modified?
        :rtype: ``bool``
        """
        return self.scene.isModified

    @property
    def canUndo(self) -> bool:
        """
        :getter: Return whether previously executed operations are saved in history
            or not.

        :rtype: ``bool``
        """
        return self.scene.history.canUndo is True

    @property
    def canRedo(self) -> bool:
        """
        :getter: Return whether the history contains cancelled operations or not.
        :rtype: ``bool``
        """
        return self.scene.history.canRedo is True

    @property
    def selectedItems(self) -> List[QGraphicsItem]:
        """
        :getter: Return :class:`~nodedge.scene.Scene`'s currently selected items.
        :rtype: ``list[QGraphicsItem]``
        """

        return self.scene.selectedItems

    @property
    def hasSelectedItems(self) -> bool:
        """
        :getter: Return ``True`` if there is selected items in the
            :class:`nodedge.node_scene.Scene`.
        :rtype: ``bool``
        """
        return self.selectedItems != []

    def updateTitle(self) -> None:
        """
        Update the ``QMainWindow``'s title with the user friendly filename.
        """
        self.setWindowTitle(self.userFriendlyFilename)

    def newFile(self) -> None:
        """
        Create a new file.
        Clear the scene and history, and reset filename.
        """
        self.scene.clear()
        self.filename = ""
        self.scene.history.clear()

    def loadFile(self, filename: str) -> bool:
        """
        Load serialized graph from JSON file.

        :param filename: file to load
        :type filename: ``str``
        :return: Operation success
        :rtype: ``bool``
        """
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            # Don't store initial stamp because the file has still not been changed.
            self.scene.history.clear()
            QApplication.restoreOverrideCursor()
            self.evalNodes()
            return True
        except FileNotFoundError as e:
            self.__logger.warning(f"File {filename} not found: {e}")
            dumpException(e)
            QMessageBox.warning(
                self,
                "Error loading %s" % os.path.basename(filename),
                str(e).replace("[Errno 2]", ""),
            )
            return False
        except InvalidFile as e:
            self.__logger.warning(f"Error loading {filename}: {e}")
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(
                self, f"Error loading {os.path.basename(filename)}", str(e)
            )
            dumpException(e)
            return False

    def saveFile(self, filename: Optional[str] = None) -> bool:
        """
        Save serialized graph to JSON file.
        When called with empty parameter, the filename is unchanged.

        :param filename: file to store the graph
        :type filename: ``str`` | ``None``
        :return: Operation success
        :rtype: ``bool``
        """
        if filename is not None:
            self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()

        return True

    def evalNodes(self) -> None:
        """
        Evaluate all the nodes present in the scene.
        """
        for node in self.scene.nodes:
            if isinstance(node, Block):
                node.eval()

    def mouseReleaseEvent(self, ev: QMouseEvent) -> None:
        """
        Handle Qt mouse's button release event.

        :param ev: Mouse release event
        :type ev: ``QMouseEvent``
        """
        self.graphicsView.mouseReleaseEvent(ev)
        super().mouseReleaseEvent(ev)

    def mousePressEvent(self, ev: QMouseEvent) -> None:
        """
        Handle Qt mouse's button press event.

        :param ev: Mouse press event
        :type ev: ``QMouseEvent``
        """
        self.graphicsView.mousePressEvent(ev)
        super().mousePressEvent(ev)

    def addDebugContent(self) -> None:
        """
        Testing method to put random QGraphicsItems and elements into QGraphicsScene
        """
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)

        rect = self.scene.graphicsScene.addRect(
            -100, -100, 80, 100, outlinePen, greenBrush
        )
        rect.setFlag(QGraphicsItem.ItemIsMovable)

    def addNodes(self) -> None:
        """
        Testing method to create 3 :class:`~nodedge.node.Node` connected by 2
        :class:`~nodedge.edge.Edge`.
        """
        node1 = Node(
            self.scene,
            "Node 1",
            inputSocketTypes=[SocketType.Any, SocketType.Number, SocketType.String],
            outputSocketTypes=[SocketType.Any],
        )
        node2 = Node(
            self.scene,
            "Node 2",
            inputSocketTypes=[SocketType.Any, SocketType.Number, SocketType.String],
            outputSocketTypes=[SocketType.Any],
        )
        node3 = Node(
            self.scene,
            "Node 3",
            inputSocketTypes=[SocketType.Any, SocketType.Number, SocketType.String],
            outputSocketTypes=[SocketType.Any],
        )

        node1.pos = (-350, -250)
        node2.pos = (-75, 100)
        node3.pos = (200, -75)

        Edge(  # noqa: F841
            self.scene,
            node1.outputSockets[0],
            node2.inputSockets[1],
            edgeType=EdgeType.BEZIER,
        )
        Edge(  # noqa: F841
            self.scene,
            node2.outputSockets[0],
            node3.inputSockets[2],
            edgeType=EdgeType.BEZIER,
        )

        self.scene.history.storeInitialStamp()

    def addCustomNode(self):
        """Testing method to create a custom Node with custom content"""

        class NNodeContent(QLabel):
            def __init__(self, parentNode, parent=None):
                super().__init__("FooBar")
                self.node = parentNode
                self.setParent(parent)

        class NNode(Node):
            NodeContentClass = NNodeContent

        self.scene.setNodeClassSelector(lambda data: NNode)
        node = NNode(self.scene, "A Custom Node 1", inputSocketTypes=[0, 1, 2])

        self.__logger.debug("Node content:", node.content)
