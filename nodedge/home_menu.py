import logging

from PySide6.QtCore import QEvent, Signal
from PySide6.QtGui import QEnterEvent, QMouseEvent
from PySide6.QtWidgets import QMenu, QMenuBar

logger = logging.getLogger(__name__)


class HomeMenu(QMenu):
    pressed = Signal()

    def __init__(self, parent):
        super(HomeMenu, self).__init__(parent)
        self.hovered = False

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.pressed.emit()
        super(HomeMenu, self).mousePressEvent(event)

    def enterEvent(self, event: QEnterEvent) -> None:
        self.hovered = True
        super(HomeMenu, self).enterEvent(event)

    def leaveEvent(self, event: QEvent) -> None:
        self.hovered = False
        super(HomeMenu, self).leaveEvent(event)


class MenuBar(QMenuBar):
    def __init__(self, parent):
        super(MenuBar, self).__init__(parent)

        self.homeMenu = HomeMenu(self)
        self.homeMenu.setTitle("&Home")

        menuAction = self.addMenu(self.homeMenu)

        menuAction.toggled.connect(self.onHomeMenuActionTriggered)

    def onHomeMenuActionTriggered(self):
        self.homeMenu.pressed.emit()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if "Home" in self.actionAt(event.pos()).text():
            self.homeMenu.pressed.emit()

        logger.debug("Menu bar pressed.")
        super(MenuBar, self).mousePressEvent(event)
