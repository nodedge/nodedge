import logging

from PyQt5.QtCore import *
from PyQt5.QtGui import *

from nodedge.editor_widget import EditorWidget


class MdiSubWindow(EditorWidget):
    def __init__(self):
        super().__init__()

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self._closeEventListeners = []

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.scene.addHasBeenModifiedListener(self.updateTitle)

        self.updateTitle()

    def addCloseEventListener(self, callback):
        self._closeEventListeners.append(callback)

    def closeEvent(self, event: QCloseEvent) -> None:
        for callback in self._closeEventListeners:
            callback(self, event)
        self.__logger.debug("Everything done in after close event")

