# -*- coding: utf-8 -*-
"""
<ModuleName> module containing :class:`~nodedge.<Name>.<ClassName>` class.
"""
import logging
import os

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPainter, QPalette, QPixmap
from PyQt5.QtWidgets import QMdiArea

from nodedge import DEBUG_ITEMS_PRESSED
from nodedge.utils import widgetsAt


class MdiArea(QMdiArea):
    itemsPressed = pyqtSignal(list)

    def __init__(self, parent=None):
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

    def paintEvent(self, event):

        painter = QPainter()
        painter.begin(self.viewport())

        if not self.centered:
            painter.drawPixmap(
                0, 0, self.width(), self.height(), self.background_pixmap
            )
        else:
            painter.fillRect(event.rect(), self.palette().color(QPalette.Window))
            x = (self.width() - self.display_pixmap.width()) / 2
            y = (self.height() - self.display_pixmap.height()) / 2
            painter.drawPixmap(x, y, self.display_pixmap)

        painter.end()

    #
    # def resizeEvent(self, event):
    #
    #     self.display_pixmap = self.background_pixmap.scaled(
    #         event.size() * 1.4, Qt.KeepAspectRatio
    #     )

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if DEBUG_ITEMS_PRESSED:
            pos = e.globalPos()
            self.__logger.debug([w.__class__.__name__ for w in widgetsAt(pos)])
            self.itemsPressed.emit([w.__class__.__name__ for w in widgetsAt(pos)])
        super().mousePressEvent(e)
