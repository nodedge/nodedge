from nodedge.edge import *
from nodedge.graphics_cutline import GraphicsCutline
from nodedge.utils import dumpException


MODE_NOOP = 1
MODE_EDGE_DRAG = 2
MODE_EDGE_CUT = 3


class GraphicsView(QGraphicsView):
    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, graphicsScene, parent=None):
        super().__init__(parent)

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.INFO)

        self.graphicsScene = graphicsScene
        self.initUI()

        self.setScene(self.graphicsScene)

        self.zoomInFactor = 1.75
        self.zoomClamp = True
        self.zoomStep = 1
        self.zoomRange = [0, 10]
        self.zoom = 10

        self.mode = MODE_NOOP
        self.lastLMBClickScenePos = None
        self.edgeStartDragThreshold = 10
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False

        self.dragEdge: (Edge, None) = None

        self.cutline = GraphicsCutline()
        self.graphicsScene.addItem(self.cutline)

        self._dragEnterListeners = []
        self._dropListeners = []

    def __repr__(self):
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
        self.setRenderHint(QPainter.Antialiasing or
                           QPainter.HighQualityAntialiasing or
                           QPainter.TextAntialiasing or
                           QPainter.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        for callback in self._dragEnterListeners:
            callback(event)

    def dropEvent(self, event: QDropEvent) -> None:
        for callback in self._dropListeners:
            callback(event)

    def addDragEnterListener(self, callback):
        self._dragEnterListeners.append(callback)

    def addDropListener(self, callback):
        self._dropListeners.append(callback)

    def mousePressEvent(self, event):
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
        if event.button() == Qt.MiddleButton:
            self.middleMouseButtonRelease(event)
        if event.button() == Qt.LeftButton:
            self.leftMouseButtonRelease(event)
        if event.button() == Qt.RightButton:
            self.rightMouseButtonRelease(event)
        else:
            super().mouseReleaseEvent(event)

    def leftMouseButtonPress(self, event):

        item = self.getItemAtClick(event)

        self.lastLMBClickScenePos = self.mapToScene(event.pos())

        self.__logger.debug("LMB "+self.debugModifiers(event)+f"{item}")

        if hasattr(item, "node") or isinstance(item, GraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mousePressEvent(fakeEvent)
                return

        if type(item) is GraphicsSocket:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGE_DRAG
                self.__logger.debug(f"Drag mode: {self.mode}")
                self.dragEdgeStart(item)
                return

        if self.mode == MODE_EDGE_DRAG:
            ret = self.dragEdgeEnd(item)
            if ret:
                self.__logger.debug("")
                return

        if item is None:
            if event.modifiers() & Qt.ControlModifier:
                self.mode = MODE_EDGE_CUT
                fakeEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton, event.modifiers())
                super().mouseReleaseEvent(fakeEvent)
                QApplication.setOverrideCursor(Qt.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonRelease(self, event):
        item = self.getItemAtClick(event)

        if hasattr(item, "node") or isinstance(item, GraphicsEdge) or item is None:
            if event.modifiers() & Qt.ShiftModifier:
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                        Qt.LeftButton, Qt.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return

        if self.mode == MODE_EDGE_DRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                ret = self.dragEdgeEnd(item)
                if ret:
                    return

        if self.mode == MODE_EDGE_CUT:
            self.cutIntersectingEdges()
            self.cutline.linePoints = []
            self.cutline.update()
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.mode = MODE_NOOP
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
        # Debug logging
        item = self.getItemAtClick(event)

        if item is None:
            self.__logger.info(self)
        elif type(item) is GraphicsSocket:
            self.__logger.info(f"\n||||{item.socket} connected to \n||||{item.socket.edges}")
        elif type(item) in [GraphicsEdgeDirect, GraphicsEdgeBezier]:
            log = f"\n||||{item.edge} connects"
            log += f"\n||||{item.edge.startSocket.node} \n||||{item.edge.endSocket.node}"

            self.__logger.info(log)

        # Faking event to enable mouse dragging the scene
        release_event = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                    Qt.LeftButton, Qt.NoButton, event.modifiers())
        super().mouseReleaseEvent(release_event)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                 Qt.LeftButton, event.buttons() | Qt.LeftButton, event.modifiers())
        super().mousePressEvent(fake_event)

    def middleMouseButtonRelease(self, event):
        fake_event = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                 Qt.LeftButton, event.buttons() & -Qt.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fake_event)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def rightMouseButtonPress(self, event):
        super().mousePressEvent(event)

    def rightMouseButtonRelease(self, event):
        super().mouseReleaseEvent(event)

    def dragEdgeStart(self, item):
        try:
            self.__logger.info("Assign socket.")
            self.dragStartSocket = item.socket
            self.dragEdge = Edge(self.graphicsScene.scene, item.socket, edgeType=EDGE_TYPE_BEZIER)
        except Exception as e:
            dumpException(e)

    def dragEdgeEnd(self, item):
        """
        :param item: selected QItem
        :return: True if we skip the rest of the code. False otherwise.
        """
        self.mode = MODE_NOOP
        self.__logger.debug(f"Drag mode: {self.mode}")

        self.dragEdge.remove()
        self.dragEdge = None

        try:
            if type(item) is GraphicsSocket:
                if item.socket != self.dragStartSocket:

                    if not self.dragStartSocket.allowsMultiEdges:
                        self.dragStartSocket.removeAllEdges()

                    if not item.socket.allowsMultiEdges:
                        item.socket.removeAllEdges()

                    newEdge = Edge(self.graphicsScene.scene, self.dragStartSocket, item.socket, edgeType=EDGE_TYPE_BEZIER)
                    item.socket.addEdge(newEdge)
                    self.__logger.debug(f"New edge created: {newEdge} connecting"
                                        f"\n|||| {newEdge.startSocket} to"
                                        f"\n |||| {newEdge.endSocket}")

                    self.graphicsScene.scene.history.store("Create a new edge by dragging")
                    self.__logger.info("Socket assigned.")
                    return True
        except Exception as e:
            dumpException(e)

        self.__logger.debug("Drag edge successful.")
        return False

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.mode == MODE_EDGE_DRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.graphicsEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.graphicsEdge.update()

        if self.mode == MODE_EDGE_CUT:
            pos = self.mapToScene(event.pos())
            self.cutline.linePoints.append(pos)
            self.cutline.update()

        self.lastSceneMousePos = self.mapToScene(event.pos())
        self.scenePosChanged.emit(int(self.lastSceneMousePos.x()), (self.lastSceneMousePos.y()))

        super().mouseMoveEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> None:
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
        # Compute zoom factor
        zoomOutFactor = 1. / self.zoomInFactor

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
        for ix in range(len(self.cutline.linePoints)-1):
            p1 = self.cutline.linePoints[ix]
            p2 = self.cutline.linePoints[ix+1]

            for edge in self.graphicsScene.scene.edges:
                if edge.graphicsEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.graphicsScene.scene.history.store("Delete cut edges.")

    def deleteSelected(self):
        for item in self.graphicsScene.selectedItems():
            if isinstance(item, GraphicsEdge):
                item.edge.remove()
            elif hasattr(item, "node"):
                item.node.remove()

        self.graphicsScene.scene.history.store("Delete selected objects.")

    def getItemAtClick(self, event):
        """" Return the object on which the user has clicked/released with a mouse button."""
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def distanceBetweenClickAndReleaseIsOff(self, event):
        """ Measure if we are too far from the last LMB click scene position. """
        newLMBClickPos = self.mapToScene(event.pos())
        distScene = newLMBClickPos - self.lastLMBClickScenePos
        edgeStartDragThresholdSquared = self.edgeStartDragThreshold ** 2
        distSceneSquared = distScene.x() * distScene.x() + distScene.y() * distScene.y()
        if distSceneSquared < edgeStartDragThresholdSquared:
            self.__logger.debug(f"Squared distance between new and last LMB click: "
                                f"{distSceneSquared} < {edgeStartDragThresholdSquared}")
            return False
        else:
            return True

    def debugModifiers(self, event):
        dlog = ""
        if event.modifiers() & Qt.ShiftModifier:
            dlog += "SHIFT "
        if event.modifiers() & Qt.ControlModifier:
            dlog += "CTRL "
        if event.modifiers() & Qt.AltModifier:
            dlog += "ALT "
        return dlog



