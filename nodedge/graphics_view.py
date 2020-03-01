# -*- coding: utf-8 -*-
"""
A module containing `Graphics View` for Nodedge
"""

import logging
from enum import IntEnum
from typing import Callable, List, Optional, cast

from PyQt5.QtCore import QEvent, QPointF, Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent, QMouseEvent, QPainter
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsView

from nodedge.edge import Edge, EdgeType
from nodedge.graphics_cut_line import GraphicsCutLine
from nodedge.graphics_edge import GraphicsEdge, GraphicsEdgeBezier, GraphicsEdgeDirect
from nodedge.graphics_scene import GraphicsScene
from nodedge.graphics_socket import GraphicsSocket
from nodedge.utils import dumpException


class DragMode(IntEnum):
    NOOP = 1  #: Mode representing ready state
    EDGE_DRAG = 2  #: Mode representing when we drag edge state
    EDGE_CUT = 3  #: Mode representing when we draw a cutting edge


#: Distance when click on socket to enable `Drag Edge`
EDGE_START_DRAG_THRESHOLD = 10


class GraphicsView(QGraphicsView):
    """Class representing Nodedge's `Graphics View`"""

    #: pyqtSignal emitted when cursor position on the `Scene` has changed
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, graphicsScene, parent=None):
        """
        :param grScene: reference to the :class:`~nodedge.graphics_scene.QDMGraphicsScene`
        :type grScene: :class:`~nodedge.graphics_scene.QDMGraphicsScene`
        :param parent: parent widget
        :type parent: ``QWidget``

        :Instance Attributes:

        - **grScene** - reference to the :class:`~nodedge.graphics_scene.QDMGraphicsScene`
        - **mode** - state of the `Graphics View`
        - **zoomInFactor**- ``float`` - zoom step scaling, default 1.25
        - **zoomClamp** - ``bool`` - do we clamp zooming or is it infinite?
        - **zoom** - current zoom step
        - **zoomStep** - ``int`` - the relative zoom step when zooming in/out
        - **zoomRange** - ``[min, max]``

        """

        super().__init__(graphicsScene)

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)

        self.graphicsScene: GraphicsScene = graphicsScene
        self.initUI()

        self.setScene(self.graphicsScene)

        self.zoomInFactor: float = 1.75
        self.zoomClamp: bool = True
        self.zoomStep: int = 1
        self.zoomRange: List[int] = [0, 10]
        self.zoom: float = 10

        self.lastSceneMousePos: QPointF = QPointF()

        self.mode: DragMode = DragMode.NOOP
        self.lastLMBClickScenePos: Optional[QPointF] = None
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False

        self.dragEdge: (Edge, None) = None

        self.cutline = GraphicsCutLine()
        self.graphicsScene.addItem(self.cutline)

        self._dragEnterListeners = []
        self._dropListeners = []

    def __str__(self):
        rep = f"\n||||Scene:"
        rep += f"\n||||Nodes:"
        for node in self.graphicsScene.scene.nodes:
            rep += f"\n||||{node}"

        rep += f"\n||||Edges:"
        for edge in self.graphicsScene.scene.edges:
            rep += f"\n||||{edge}"
        rep += "\n||||"

        return rep

    def initUI(self):
        """Set up this ``QGraphicsView``"""
        self.setRenderHint(
            QPainter.Antialiasing
            or QPainter.HighQualityAntialiasing
            or QPainter.TextAntialiasing
            or QPainter.SmoothPixmapTransform
        )
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Trigger our registered `Drag Enter` events"""
        for callback in self._dragEnterListeners:
            callback(event)

    def dropEvent(self, event: QDropEvent) -> None:
        """Trigger our registered `Drop` events"""
        for callback in self._dropListeners:
            callback(event)

    def addDragEnterListener(self, callback: Callable[[QDragEnterEvent], None]):
        """
        Register callback for `Drag Enter` event

        :param callback: callback function
        """

        self._dragEnterListeners.append(callback)

    def addDropListener(self, callback: Callable[[QDropEvent], None]):
        """
        Register callback for `Drop` event

        :param callback: callback function
        """
        self._dropListeners.append(callback)

    def mousePressEvent(self, event):
        """Dispatch Qt's mousePress event to corresponding function below"""
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.LeftButton:
            try:
                self.leftMouseButtonPress(event)
            except Exception as e:
                dumpException(e)
        elif event.button() == Qt.RightButton:
            self.rightMouseButtonPress(event)

        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        """Dispatch Qt's mouseRelease event to corresponding function below"""
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        if event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def leftMouseButtonPress(self, event):
        """Slot called when the left mouse button was pressed"""
        try:
            item = self.getItemAtClick(event)

            self.lastLMBClickScenePos = self.mapToScene(event.pos())

            self.__logger.debug("LMB " + self.debugModifiers(event) + f"{item}")

            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(
                    QEvent.MouseButtonPress,
                    event.localPos(),
                    event.screenPos(),
                    Qt.LeftButton,
                    event.buttons() | Qt.LeftButton,
                    event.modifiers() | Qt.ControlModifier,
                )
                super().mousePressEvent(fakeEvent)
                return

            if type(item) is GraphicsSocket and self.mode == DragMode.NOOP:
                self.mode = DragMode.EDGE_DRAG
                self.__logger.debug(f"Drag mode: {self.mode}")
                self.dragEdgeStart(item)
                return

            if self.mode == DragMode.EDGE_DRAG:
                ret = self.dragEdgeEnd(item)
                if ret:
                    self.__logger.debug("")
                    return

            if item is None:
                if event.modifiers() & Qt.ControlModifier:
                    self.mode = DragMode.EDGE_CUT
                    fakeEvent = QMouseEvent(
                        QEvent.MouseButtonRelease,
                        event.localPos(),
                        event.screenPos(),
                        Qt.LeftButton,
                        Qt.NoButton,
                        event.modifiers(),
                    )
                    super().mouseReleaseEvent(fakeEvent)
                    QApplication.setOverrideCursor(Qt.CrossCursor)
                    return
                else:
                    self.rubberBandDraggingRectangle = True

            super().mousePressEvent(event)
        except Exception as e:
            dumpException(e)

    def leftMouseButtonRelease(self, event):
        """When Left  mouse button was released"""
        item = self.getItemAtClick(event)

        if event.modifiers() & Qt.ShiftModifier:
            event.ignore()
            fakeEvent = QMouseEvent(
                event.type(),
                event.localPos(),
                event.screenPos(),
                Qt.LeftButton,
                Qt.NoButton,
                event.modifiers() | Qt.ControlModifier,
            )
            super().mouseReleaseEvent(fakeEvent)
            return

        if (
            self.mode == DragMode.EDGE_DRAG
            and self.distanceBetweenClickAndReleaseIsOff(event)
        ):
            ret = self.dragEdgeEnd(item)
            if ret:
                return

        if self.mode == DragMode.EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutline.linePoints = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = DragMode.NOOP
            return

        if self.rubberBandDraggingRectangle:
            self.rubberBandDraggingRectangle = False
            # self.graphicsScene.scene.history.store("Change selection", sceneIsModified=False)
            selectedItems = self.graphicsScene.selectedItems()
            if not selectedItems:
                self.graphicsScene.itemsDeselected.emit()

            if selectedItems != self.graphicsScene.scene.lastSelectedItems:
                self.graphicsScene.itemSelected.emit()
            return

        super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        """When Middle mouse button was pressed"""
        # Debug logging
        item = self.getItemAtClick(event)

        if item is None:
            self.__logger.info(self)
        elif type(item) is GraphicsSocket:
            self.__logger.info(
                f"\n||||{item.socket} connected to \n||||{item.socket.edges}"
            )
        elif type(item) in [GraphicsEdgeDirect, GraphicsEdgeBezier]:
            log = f"\n||||{item.edge} connects"
            log += f"\n||||{item.edge.sourceSocket.node} \n||||{item.edge.destinationSocket.node}"

            self.__logger.info(log)

        # Faking event to enable mouse dragging the scene
        release_event = QMouseEvent(
            QEvent.MouseButtonRelease,
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            Qt.NoButton,
            event.modifiers(),
        )
        super().mouseReleaseEvent(release_event)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fake_event = QMouseEvent(
            event.type(),
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            event.buttons() | Qt.LeftButton,
            event.modifiers(),
        )
        super().mousePressEvent(fake_event)

    def middleMouseButtonRelease(self, event):
        """When Middle mouse button was released"""
        fake_event = QMouseEvent(
            event.type(),
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            event.buttons() & -Qt.LeftButton,
            event.modifiers(),
        )
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def rightMouseButtonPress(self, event):
        """When Right mouse button was pressed"""
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        """When Right mouse button was release"""
        super().mouseReleaseEvent(event)

    def dragEdgeStart(self, item):
        """Code handling the start of dragging an `Edge` operation"""
        try:
            self.__logger.debug("Assign socket.")
            self.dragStartSocket = item.socket
            self.dragEdge = Edge(
                self.graphicsScene.scene, item.socket, edgeType=EdgeType.BEZIER
            )
        except Exception as e:
            dumpException(e)

    def dragEdgeEnd(self, item: QGraphicsItem):
        """Code handling the end of dragging an `Edge` operation. In this code return True if skip the
        rest of the mouse event processing

        :param item: Item in the `Graphics Scene` where we ended dragging an `Edge`
        :type item: ``QGraphicsItem``
        """
        self.mode = DragMode.NOOP
        self.__logger.debug(f"Drag mode: {self.mode}")

        self.dragEdge.remove()
        self.dragEdge = None

        try:
            if (
                type(item) is GraphicsSocket
                and cast(GraphicsSocket, item).socket != self.dragStartSocket
            ):
                item = cast(GraphicsSocket, item)

                if not self.dragStartSocket.allowsMultiEdges:
                    self.dragStartSocket.removeAllEdges()

                if not item.socket.allowsMultiEdges:
                    item.socket.removeAllEdges()

                newEdge = Edge(
                    self.graphicsScene.scene,
                    self.dragStartSocket,
                    item.socket,
                    edgeType=EdgeType.BEZIER,
                )
                item.socket.addEdge(newEdge)
                self.__logger.debug(
                    f"New edge created: {newEdge} connecting"
                    f"\n|||| {newEdge.sourceSocket} to"
                    f"\n |||| {newEdge.destinationSocket}"
                )

                for socket in [self.dragStartSocket, item.socket]:
                    socket.node.onEdgeConnectionChanged(newEdge)

                    if socket.isInput:
                        socket.node.onInputChanged(newEdge)

                self.graphicsScene.scene.history.store("Create a new edge by dragging")
                self.__logger.debug("Socket assigned.")
                return True
        except Exception as e:
            dumpException(e)

        self.__logger.debug("Drag edge successful.")
        return False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Overriden Qt's ``mouseMoveEvent`` handling Scene/View logic"""
        if self.mode == DragMode.EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.graphicsEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.graphicsEdge.update()

        if self.mode == DragMode.EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.linePoints.append(pos)
            self.cutline.update()

        self.lastSceneMousePos = self.mapToScene(event.pos())
        self.scenePosChanged.emit(
            int(self.lastSceneMousePos.x()), (self.lastSceneMousePos.y())
        )

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
            .. note::
                This overriden Qt's method was used for handling key shortcuts, before we implemented propper
                ``QWindow`` with Actions and Menu. Still the commented code serves as an example how to handle
                key presses without Qt's framework for Actions and shortcuts. There can be also found an example
                how to solve the problem when Node does contain Text/LineEdit and we press `Delete`
                key (also serving to delete `Node`)

            :param event: Qt's Key event
            :type event: ``QKeyEvent``
            :return:
            """

        # if event.key() == Qt.Key_Delete:
        #     if not self.editingFlag:
        #         self.deleteSelected()
        #     else:
        #         super().keyPressEvent(event)
        # elif event.key() == Qt.Key_S and event.modifiers() & Qt.ControlModifier:
        #     self.graphicsScene.scene.saveToFile("graph.json")
        # elif event.key() == Qt.Key_O and event.modifiers() & Qt.ControlModifier:
        #     self.graphicsScene.scene.loadFromFile("graph.json")
        # elif event.key() == Qt.Key_1:
        #     self.graphicsScene.scene.history.store("A")
        # elif event.key() == Qt.Key_2:
        #     self.graphicsScene.scene.history.store("B")
        # elif event.key() == Qt.Key_3:
        #     self.graphicsScene.scene.history.store("C")
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier \
        #         and not event.modifiers() & Qt.ShiftModifier:
        #     self.graphicsScene.scene.history.undo()
        # elif event.key() == Qt.Key_Z and event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.ShiftModifier:
        #     self.graphicsScene.scene.history.redo()
        if event.key() == Qt.Key_H:
            self.__logger.info(f"{self.graphicsScene.scene.history}")

        else:
            super().keyPressEvent(event)

    def wheelEvent(self, event):
        """overriden Qt's ``wheelEvent``. This handles zooming"""
        # Compute zoom factor
        zoomOutFactor = 1.0 / self.zoomInFactor

        # Compute zoom
        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]:
            self.zoom = self.zoomRange[0]
            clamped = True
        elif self.zoom > self.zoomRange[1]:
            self.zoom = self.zoomRange[1]
            clamped = True

        # Set scene scale
        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)

    def cutIntersectingEdges(self):
        """Compare which `Edges` intersect with current `Cut line` and delete them safely"""
        for ix in range(len(self.cutline.linePoints) - 1):
            p1 = self.cutline.linePoints[ix]
            p2 = self.cutline.linePoints[ix + 1]

            for edge in self.graphicsScene.scene.edges:
                if edge.graphicsEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.graphicsScene.scene.history.store("Delete cut edges.")

    def deleteSelected(self):
        """Shortcut for safe deleting every object selected in the `Scene`."""
        for item in self.graphicsScene.selectedItems():
            if isinstance(item, GraphicsEdge):
                item.edge.remove()
            elif hasattr(item, "node"):
                item.node.remove()

        self.graphicsScene.scene.history.store("Delete selected objects.")

    def getItemAtClick(self, event):
        """Return the object on which we've clicked/release mouse button

        :param event: Qt's mouse or key event
        :type event: ``QEvent``
        :return: ``QGraphicsItem`` which the mouse event happened or ``None``
        """
        pos = event.pos()
        return self.itemAt(pos)

    def distanceBetweenClickAndReleaseIsOff(self, event):
        """ Measures if we are too far from the last Mouse button click scene position.
        This is used for detection if we release too far after we clicked on a `Socket`

        :param event: Qt's mouse event
        :type event: ``QMouseEvent``
        :return: ``True`` if we released too far from where we clicked before
        """
        newLMBClickPos = self.mapToScene(event.pos())
        distScene = newLMBClickPos - self.lastLMBClickScenePos
        edgeStartDragThresholdSquared = EDGE_START_DRAG_THRESHOLD ** 2
        distSceneSquared = distScene.x() * distScene.x() + distScene.y() * distScene.y()
        if distSceneSquared < edgeStartDragThresholdSquared:
            self.__logger.debug(
                f"Squared distance between new and last LMB click: "
                f"{distSceneSquared} < {edgeStartDragThresholdSquared}"
            )
            return False
        else:
            return True

    def debugModifiers(self, event):
        """Helper function get string if we hold Ctrl, Shift or Alt modifier keys"""
        dlog = ""
        if event.modifiers() & Qt.ShiftModifier:
            dlog += "SHIFT "
        if event.modifiers() & Qt.ControlModifier:
            dlog += "CTRL "
        if event.modifiers() & Qt.AltModifier:
            dlog += "ALT "
        return dlog
