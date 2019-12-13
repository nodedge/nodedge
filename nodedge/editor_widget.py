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

    def shortFilename(self):
        name = os.path.basename(self.filename) if self.hasName() else "New graph"
        # TODO: Add * hasBeenModified here
        return name

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

    def addDebugContent(self):
        green_brush = QBrush(Qt.green)
        outline_pen = QPen(Qt.black)
        outline_pen.setWidth(2)

        rectangle = self.graphicsScene.addRect(-100, -100, 80, 100, outline_pen, green_brush)
        rectangle.setFlag(QGraphicsItem.ItemIsMovable)
        rectangle.setFlag(QGraphicsItem.ItemIsSelectable)

        text = self.graphicsScene.addText("Welcome in Nodedge!", QFont("Ubuntu"))
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setDefaultTextColor(QColor.fromRgbF(1., 1., 1.))

        widget1 = QPushButton("Show shortcuts")
        proxy1 = self.graphicsScene.addWidget(widget1)
        proxy1.setFlag(QGraphicsItem.ItemIsMovable)
        proxy1.setPos(0, 100)

        widget2 = QTextEdit()
        proxy2 = self.graphicsScene.addWidget(widget2)
        proxy2.setFlag(QGraphicsItem.ItemIsMovable)
        proxy2.setPos(100, 0)

    def loadStyleSheet(self, fileName):
        print(f"Style loading: {fileName}")
        file = QFile(fileName)
        file.open(QFile.ReadOnly or QFile.Text)
        styleSheet = file.readAll()
        QApplication.instance().setStyleSheet(str(styleSheet, encoding="utf-8"))

