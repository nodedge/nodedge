from nodedge.editor_widget import EditorWidget
from PyQt5.QtCore import *


class MdiSubWindow(EditorWidget):
    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WA_DeleteOnClose)

        self.scene.addHasBeenModifiedListener(self.updateTitle)

        self.updateTitle()
