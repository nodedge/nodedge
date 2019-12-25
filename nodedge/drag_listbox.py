import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


class DragListbox(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.iconSize = QSize(32, 32)
        self.setIconSize(self.iconSize)

        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)

        self.addNodes()

    def addNodes(self):
        nodesIconPath = f"{os.path.dirname(__file__)}/resources/node_icons"

        self.addNode("Input", f"{nodesIconPath}/in.png")
        self.addNode("Ouput", f"{nodesIconPath}/out.png")
        self.addNode("Add", f"{nodesIconPath}/add.png")
        self.addNode("Substract", f"{nodesIconPath}/subtract.png")
        self.addNode("Multiply", f"{nodesIconPath}/multiply.png")
        self.addNode("Divide", f"{nodesIconPath}/divide.png")

    def addNode(self, name, iconPath=None, operationCode=0):
        item = QListWidgetItem(name, self)
        pixmap = QPixmap(iconPath) if iconPath else "."
        item.setIcon(QIcon(pixmap))
        item.setSizeHint(self.iconSize)

        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled)

        item.setData(Qt.UserRole, pixmap)
        item.setData(Qt.UserRole+1, operationCode)
