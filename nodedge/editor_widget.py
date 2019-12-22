from nodedge.scene import Scene, InvalidFile
from nodedge.graphics_view import GraphicsView
from nodedge.node import Node
from nodedge.edge import *
import os


class EditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

        self.filename = None

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        # Create graphics view
        self.scene = Scene()

        # Add content
        self.addNodes()

        self.view = GraphicsView(self.scene.graphicsScene, self)
        self.layout.addWidget(self.view)

        # self.addDebugContent()

    def hasName(self):
        return self.filename is not None

    @property
    def shortName(self):
        return os.path.basename(self.filename)

    @property
    def userFriendlyFilename(self):
        name = os.path.basename(self.filename) if self.hasName() else "New graph"
        # TODO: Add * hasBeenModified here
        return name + ("*" if self.isModified() else "")

    def addNodes(self):
        inputs = [1, 2, 3]
        outputs = [1]
        node1 = Node(self.scene, "My Mew Node!", inputs=inputs, outputs=outputs)
        node2 = Node(self.scene, "My Mew Node!", inputs=inputs, outputs=outputs)
        node3 = Node(self.scene, "My Mew Node!", inputs=inputs, outputs=outputs)

        node1.setPos(-350, -250)
        node2.setPos(-75, -0)
        node3.setPos(200, -50)

        edge1 = Edge(self.scene, node1.outputs[0], node2.inputs[1], edgeType=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[0], node3.inputs[2], edgeType=EDGE_TYPE_BEZIER)

    def isModified(self):
        return self.scene.isModified

    def loadFile(self, filename):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(filename)
            self.filename = filename
            # Clear history
            QApplication.restoreOverrideCursor()
            return True
        except InvalidFile as e:
            self.__logger.warning(f"Error loading {filename}: {e}")
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, f"Error loading {os.path.basename(filename)}", str(e))
            return False
        finally:
            pass

    def saveFile(self, filename=None):
        # When called with empty parameter, don't store the filename
        if filename is not None:
            self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()

        return True

    def updateTitle(self):
        self.setWindowTitle(self.userFriendlyFilename)
