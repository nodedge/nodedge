from nodedge.editor_widget import EditorWidget
from PyQt5.QtCore import *


class MdiSubWindow(EditorWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.scene.addHasBeenModifiedListener(self.updateTitle)

        self.updateTitle()

    def updateTitle(self):
        self.setWindowTitle(self.userFriendlyFilename())
