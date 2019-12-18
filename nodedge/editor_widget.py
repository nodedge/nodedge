from nodedge.scene import Scene
from nodedge.graphics_view import GraphicsView
from nodedge.node import Node
from nodedge.edge import *
import os


class EditorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.styleSheetFileName = "qss/nodestyle.qss"
        self.loadStyleSheet(self.styleSheetFileName)

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

    def loadStyleSheet(self, fileName):
        print(f"Style loading: {fileName}")
        file = QFile(fileName)
        file.open(QFile.ReadOnly or QFile.Text)
        styleSheet = file.readAll()
        QApplication.instance().setStyleSheet(str(styleSheet, encoding="utf-8"))

    def isModified(self):
        return self.scene.isModified
