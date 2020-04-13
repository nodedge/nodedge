# -*- coding: utf-8 -*-
"""
Graphics View module containing :class:`~nodedge.graphics_view.GraphicsView`
and :class:`~nodedge.graphics_view.DragMode` classes.
"""

import logging
from enum import IntEnum
from typing import Callable, List, Optional, cast

from PyQt5.QtCore import QEvent, QPointF, Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QKeyEvent, QMouseEvent, QPainter
from PyQt5.QtWidgets import QApplication, QGraphicsItem, QGraphicsView, QWidget

from nodedge.edge import Edge, EdgeType
from nodedge.graphics_cut_line import GraphicsCutLine
from nodedge.graphics_edge import GraphicsEdge, GraphicsEdgeBezier, GraphicsEdgeDirect
from nodedge.graphics_scene import GraphicsScene
from nodedge.graphics_socket import GraphicsSocket
from nodedge.socket import Socket
from nodedge.utils import dumpException


class DragMode(IntEnum):
    """
    :class:`~nodedge.graphics_view.DragMode` class.
    """

    NOOP = 1  #: Mode representing ready state
    EDGE_DRAG = 2  #: Mode representing when we drag edge state
    EDGE_CUT = 3  #: Mode representing when we draw a cutting edge


#: Distance when click on socket to enable `Drag Edge`
EDGE_START_DRAG_THRESHOLD = 10


class GraphicsView(QGraphicsView):
    """:class:`~nodedge.graphics_view.GraphicsView` class."""

    #: pyqtSignal emitted when cursor position on the `Scene` has changed
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, graphicsScene: GraphicsScene, parent: Optional[QWidget] = None):
        """
        :param graphicsScene: reference to the :class:`~nodedge.graphics_scene.GraphicsScene`
        :type graphicsScene: :class:`~nodedge.graphics_scene.GraphicsScene`
        :param parent: parent widget
        :type parent: ``Optional[QWidget]``
        """
        super().__init__(graphicsScene, parent)

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
        self.editingFlag: bool = False
        self.rubberBandDraggingRectangle: bool = False

        self.dragEdge: Optional[Edge] = None
        self.dragStartSocket: Optional[Socket] = None

        self.cutline = GraphicsCutLine()
        self.graphicsScene.addItem(self.cutline)

        self._dragEnterListeners: List[Callable] = []
        self._dropListeners: List[Callable] = []

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
        """
        Set up this :class:`~nodedge.graphics_view.GraphicsView`.
        """
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
        """
        Handle Qt's mouse's drag enter event.

        Call all the listeners of that event.

        :param event: Mouse drag enter event
        :type event: ``QDragEnterEvent``
        """
        for callback in self._dragEnterListeners:
            callback(event)

    def dropEvent(self, event: QDropEvent) -> None:
        """
        Handle Qt's mouse's drop event.

        Call all the listeners of that event.

        :param event: Mouse drop event
        :type event: ``QDropEvent``
        """
        for callback in self._dropListeners:
            callback(event)

    def addDragEnterListener(self, callback: Callable[[QDragEnterEvent], None]):
        """
        Register callback for `Drag Enter` event.

        :param callback: callback function
        """
        self._dragEnterListeners.append(callback)

    def addDropListener(self, callback: Callable[[QDropEvent], None]):
        """
        Register callback for `Drop` event.

        :param callback: callback function
        """
        self._dropListeners.append(callback)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Dispatch Qt's `mousePressEvent` to corresponding function below.
        """
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

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        Dispatch Qt's mouseReleaseEvent to corresponding function below.
        """
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        if event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def leftMouseButtonPress(self, event: QMouseEvent):
        """
        Handle when the left mouse button is pressed.
        """
        try:
            item = self.getItemAtClick(event)
            self.__logger.debug(f"Selected object class: {item.__class__.__name__}")

            self.lastLMBClickScenePos = self.mapToScene(event.pos())

            self.__logger.debug("LMB " + self.debugModifiers(event) + f"{item}")

            if event.modifiers() & Qt.ShiftModifier:  # type: ignore
                event.ignore()
                fakeEvent = QMouseEvent(  # type: ignore
                    QEvent.MouseButtonPress,
                    event.localPos(),
                    event.screenPos(),
                    Qt.LeftButton,
                    event.buttons() | Qt.LeftButton,  # type: ignore
                    event.modifiers() | Qt.ControlModifier,  # type: ignore
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
                if event.modifiers() & Qt.ControlModifier:  # type: ignore
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

    def leftMouseButtonRelease(self, event: QMouseEvent):
        """
        Handle when left mouse button is released.
        """
        item = self.getItemAtClick(event)

        if event.modifiers() & Qt.ShiftModifier:  # type: ignore
            event.ignore()
            fakeEvent = QMouseEvent(  # type: ignore
                event.type(),
                event.localPos(),
                event.screenPos(),
                Qt.LeftButton,
                Qt.NoButton,
                event.modifiers() | Qt.ControlModifier,  # type: ignore
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
            # self.graphicsScene.scene.history.store("Change selection",
            # sceneIsModified=False)
            selectedItems = self.graphicsScene.selectedItems()
            if not selectedItems:
                self.graphicsScene.itemsDeselected.emit()

            if selectedItems != self.graphicsScene.scene.lastSelectedItems:
                self.graphicsScene.itemSelected.emit()
            return

        super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event: QMouseEvent):
        """
        Handle when middle mouse button is pressed.
        """
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
            log += (
                f"\n||||{item.edge.sourceSocket.node} \n||||"
                f"{item.edge.targetSocket.node}"
            )

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
        fake_event = QMouseEvent(  # type: ignore
            event.type(),
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            event.buttons() | Qt.LeftButton,  # type: ignore
            event.modifiers(),
        )
        super().mousePressEvent(fake_event)

    def middleMouseButtonRelease(self, event: QMouseEvent):
        """
        Handle when middle mouse button is released.
        """
        fake_event = QMouseEvent(  # type: ignore
            event.type(),
            event.localPos(),
            event.screenPos(),
            Qt.LeftButton,
            event.buttons() & -Qt.LeftButton,  # type: ignore
            event.modifiers(),
        )
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def rightMouseButtonPress(self, event: QMouseEvent):
        """
        Handle when right mouse button was pressed
        """
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event: QMouseEvent):
        """
        Handle when right mouse button is released.
        """
        super().mouseReleaseEvent(event)

    def dragEdgeStart(self, item):
        """
        Handle the start of dragging an :class:`~nodedge.edge.Edge` operation.
        """
        try:
            self.__logger.debug("Assign socket.")
            self.dragStartSocket = item.socket
            self.dragEdge = Edge(
                self.graphicsScene.scene, item.socket, edgeType=EdgeType.BEZIER
            )
        except Exception as e:
            dumpException(e)

    def dragEdgeEnd(self, item: QGraphicsItem):
        """
        Handle the end of dragging an :class:`~nodedge.edge.Edge` operation.

        :param item: Item in the `Graphics Scene` where we ended dragging an :class:`~nodedge.edge.Edge`
        :type item: ``QGraphicsItem``
        :return: True is the operation is a success, false otherwise.
        :rtype: ``bool``
        """
        self.mode = DragMode.NOOP
        self.__logger.debug(f"Drag mode: {self.mode}")

        try:
            self.dragEdge.remove()  # type: ignore
        except Exception:
            self.__logger.warning("Impossible to remove dragEdge")
        self.dragEdge = None

        try:
            if (
                type(item) is GraphicsSocket
                and cast(GraphicsSocket, item).socket != self.dragStartSocket
            ):
                item = cast(GraphicsSocket, item)

                if (
                    self.dragStartSocket is not None
                    and not self.dragStartSocket.allowMultiEdges
                ):
                    self.dragStartSocket.removeAllEdges()

                if not item.socket.allowMultiEdges:
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
                    f"\n |||| {newEdge.targetSocket}"
                )

                socket: Optional[Socket]
                for socket in [self.dragStartSocket, item.socket]:
                    if socket is not None:
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
        """
        Overridden Qt's ``mouseMoveEvent`` handling Scene/View logic
        """
        if self.mode == DragMode.EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            if self.dragEdge is not None:
                self.dragEdge.graphicsEdge.targetPos = pos
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
        Handle key shortcuts, for example to display the scene's history in the console.

        :param event: Qt's Key event
        :type event: ``QKeyEvent``
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
        """
        Overridden Qt's ``wheelEvent``.
        This handles zooming.
        """
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
        """
        Compare which :class:`~nodedge.edge.Edge`s intersect with current
        :class:`~nodedge.graphics_cut_line.GraphicsCutLine` and delete them safely.
        """
        for ix in range(len(self.cutline.linePoints) - 1):
            p1 = self.cutline.linePoints[ix]
            p2 = self.cutline.linePoints[ix + 1]

            for edge in self.graphicsScene.scene.edges:
                if edge.graphicsEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.graphicsScene.scene.history.store("Delete cut edges.")

    def deleteSelected(self):
        """
        Shortcut for safe deleting every object selected in the :class:`~nodedge.scene.Scene`.
        """
        for item in self.graphicsScene.selectedItems():
            if isinstance(item, GraphicsEdge):
                item.edge.remove()
            elif hasattr(item, "node"):
                item.node.remove()

        self.graphicsScene.scene.history.store("Delete selected objects.")

    def getItemAtClick(self, event: QMouseEvent):
        """
        Return the object on which the user clicked/released the mouse button.

        :param event: Qt's mouse or key event
        :type event: ``QMouseEvent``
        :return: Graphical item present at the clicked/released position.
        :rtype: ``QGraphicsItem`` | ``None``
        """
        pos = event.pos()
        return self.itemAt(pos)

    def distanceBetweenClickAndReleaseIsOff(self, event):
        """
        Measure if we are too far from the last mouse button click scene position.
        This is used for detection if the release is too far after the user clicked on a :class:`~nodedge.socket.Socket`

        :param event: Qt's mouse event
        :type event: ``QMouseEvent``
        :return: ``True`` if we released too far from where we clicked before, ``False`` otherwise.
        :rtype: ``bool``
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
        """
        Get the name of the pressed modifier.

        :return: "CTRL" / "SHIFT" / "ALT"
        :rtype: ``str``
        """
        dlog = ""
        if event.modifiers() & Qt.ShiftModifier:
            dlog += "SHIFT "
        if event.modifiers() & Qt.ControlModifier:
            dlog += "CTRL "
        if event.modifiers() & Qt.AltModifier:
            dlog += "ALT "
        return dlog
