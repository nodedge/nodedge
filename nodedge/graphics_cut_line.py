# -*- coding: utf-8 -*-
"""Graphics cut line module containing
:class:`~nodedge.graphics_cut_line.GraphicsCutLine` class. """
import logging
from enum import IntEnum
from typing import List, Optional

from PySide6.QtCore import QEvent, QPointF, QRectF, Qt
from PySide6.QtGui import QMouseEvent, QPainter, QPainterPath, QPen, QPolygonF
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QWidget,
)

from nodedge.utils import dumpException


class CutLineMode(IntEnum):
    """
    :class:`~nodedge.graphics_cut_line.CutLineMode` class.
    """

    NOOP = 1  #: Mode representing ready state
    CUTTING = 2  #: Mode representing when we draw a cutting edge


class CutLine:
    """
    :class:`~nodedge.graphics_cut_line.CutLine` class.
    """

    def __init__(self, graphicsView: "GraphicsView") -> None:  # type: ignore

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)
        self.mode: CutLineMode = CutLineMode.NOOP
        self.graphicsCutLine: GraphicsCutLine = GraphicsCutLine()
        self.graphicsView = graphicsView
        self.graphicsView.graphicsScene.addItem(self.graphicsCutLine)

    def update(self, event: QMouseEvent) -> Optional[QMouseEvent]:
        """
        Update the state machine of the cut line as well as the graphics cut line.

        :param event: Event triggering the update
        :type event: ``QMouseEvent``
        :return: Optional modified event needed by
            :class:`~nodedge.graphics_view.GraphicsView`
        :rtype: Optional[QMouseEvent]
        """
        eventButton: Qt.MouseButton = event.button()
        eventType: QEvent.Type = event.type()
        eventScenePos = self.graphicsView.mapToScene(event.pos())
        eventModifiers: Qt.KeyboardModifiers = event.modifiers()  # type: ignore
        if self.mode == CutLineMode.NOOP:
            if (
                eventType == QEvent.MouseButtonPress
                and eventButton == Qt.LeftButton
                and eventModifiers & Qt.ControlModifier
            ):

                self.mode = CutLineMode.CUTTING
                QApplication.setOverrideCursor(Qt.CrossCursor)

                return QMouseEvent(
                    QEvent.MouseButtonRelease,
                    event.localPos(),
                    event.screenPos(),
                    Qt.LeftButton,
                    Qt.NoButton,
                    event.modifiers(),
                )

        if self.mode == CutLineMode.CUTTING:
            if event.type() == QEvent.MouseMove:
                self.graphicsCutLine.linePoints.append(eventScenePos)
                self.graphicsCutLine.update()
            elif (
                eventType == QEvent.MouseButtonRelease and eventButton == Qt.LeftButton
            ):
                self.cutIntersectingEdges()
                self.graphicsCutLine.linePoints = []
                self.graphicsCutLine.update()
                QApplication.setOverrideCursor(Qt.ArrowCursor)
                self.mode = CutLineMode.NOOP

        return None

    def cutIntersectingEdges(self) -> None:
        """
        Compare which :class:`~nodedge.edge.Edge`s intersect with current
        :class:`~nodedge.graphics_cut_line.GraphicsCutLine` and delete them safely.
        """
        try:
            scene: "Scene" = self.graphicsView.graphicsScene.scene  # type: ignore
            self.__logger.debug(f"Cutting points: {self.graphicsCutLine.linePoints}")
            for ix in range(len(self.graphicsCutLine.linePoints) - 1):
                p1 = self.graphicsCutLine.linePoints[ix]
                p2 = self.graphicsCutLine.linePoints[ix + 1]

                # @TODO: Notify intersecting edges once.
                #  we could collect all touched nodes, and notify them once after
                #  all edges removed we could cut 3 edges leading to a single editor
                #  this will notify it 3x maybe we could use some Notifier class with
                #  methods collect() and dispatch()

                for edge in reversed(scene.edges):
                    if edge.graphicsEdge.intersectsWith(p1, p2):
                        self.__logger.debug(
                            f"[{p1.__pos__()}, {p2.__pos__()}] intersects with: {edge}"
                        )
                        edge.remove()
                    else:
                        self.__logger.debug(
                            f"[{p1.__pos__()}, {p2.__pos__()}] does not intersect with: "
                            f"{edge.graphicsEdge.path()}"
                        )

            scene.history.store("Delete cut edges.")
            self.__logger.debug("Cutting has been done.")

        except Exception as e:
            self.__logger.debug("e")
            dumpException(e)


class GraphicsCutLine(QGraphicsItem):
    """:class:`~nodedge.graphics_cut_line.GraphicsCutLine` class

    Cutting Line used for cutting multiple `Edges` with one stroke"""

    def __init__(self, parent: Optional[QGraphicsItem] = None) -> None:
        """
        :param parent: parent widget
        :type parent: ``Optional[QGraphicsItem]``
        """

        super().__init__(parent)

        self.linePoints: List[QPointF] = []
        p = QApplication.palette()
        self._pen: QPen = QPen(p.link().color())
        self._pen.setWidth(2)
        self._pen.setDashPattern([2, 4])

        self.setZValue(2)

    def boundingRect(self) -> QRectF:
        """
        Define Qt' bounding rectangle
        """
        return self.shape().boundingRect()

    def shape(self) -> QPainterPath:
        """
        Calculate the ``QPainterPath`` object from list of line points.

        :return: shape function returning ``QPainterPath`` representation of cut line
        :rtype: ``QPainterPath``
        """

        if len(self.linePoints) > 1:
            path = QPainterPath(self.linePoints[0])
            for point in self.linePoints[1:]:
                path.lineTo(point)
        else:
            path = QPainterPath(QPointF(0, 0))
            path.lineTo(QPointF(1, 1))

        return path

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,
        widget: Optional[QWidget] = None,
    ) -> None:
        """
        Paint the cut line
        """
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(self._pen)

        poly = QPolygonF(self.linePoints)
        painter.drawPolyline(poly)
