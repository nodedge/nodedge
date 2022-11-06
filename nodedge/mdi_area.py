# -*- coding: utf-8 -*-
"""
mdi_area module containing :class:`~nodedge.mdi_area.MdiArea` class.
"""
import logging
import os

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QMouseEvent, QPainter, QPaintEvent, QPalette, QPixmap
from PySide6.QtWidgets import QMdiArea

from nodedge import DEBUG_ITEMS_PRESSED
from nodedge.utils import widgetsAt


class MdiArea(QMdiArea):
    """
    :class:`~nodedge.mdi_area.MdiArea` class.
    """

    itemsPressed = Signal(list)

    def __init__(self, parent=None) -> None:
        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

        QMdiArea.__init__(self, parent)
        self.background_pixmap = QPixmap(
            os.path.join(os.path.dirname(__file__), "resources/background_mdiarea2.png")
        )
        self.centered = True

        scale = 2
        self.display_pixmap = self.background_pixmap.scaled(
            QSize(1024 * scale, 768 * scale), Qt.KeepAspectRatio
        )
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setViewMode(QMdiArea.TabbedView)
        self.setDocumentMode(True)
        self.setTabsClosable(True)
        self.setTabsMovable(True)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Qt paint event handle.

        :param event:
        :type event: ``QPaintEvent.py``
        """

        painter = QPainter()
        painter.begin(self.viewport())

        if not self.centered:
            painter.drawPixmap(
                0, 0, self.width(), self.height(), self.background_pixmap
            )
        else:
            painter.fillRect(event.rect(), self.palette().color(QPalette.Window))
            x: int = (self.width() - self.display_pixmap.width()) // 2
            y: int = (self.height() - self.display_pixmap.height()) // 2
            painter.drawPixmap(x, y, self.display_pixmap)

        painter.end()

    #
    # def resizeEvent(self, event):
    #
    #     self.display_pixmap = self.background_pixmap.scaled(
    #         event.size() * 1.4, Qt.KeepAspectRatio
    #     )

    def mousePressEvent(self, e: QMouseEvent) -> None:
        """
        Qt mouse press handle.

        :param e:
        :type e: ``QMouseEvent``
        """
        if DEBUG_ITEMS_PRESSED:
            pos = e.globalPos()
            self.__logger.debug([w.__class__.__name__ for w in widgetsAt(pos)])
            # noinspection PyUnresolvedReferences
            self.itemsPressed.emit([w.__class__.__name__ for w in widgetsAt(pos)])
        super().mousePressEvent(e)
