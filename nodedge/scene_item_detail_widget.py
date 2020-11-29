# -*- coding: utf-8 -*-
"""
Scene item detail widget module containing
:class:`~nodedge.scene_item_detail_widget.SceneItemDetailWidget` class.
"""
import logging

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QGridLayout, QLabel, QLineEdit, QSizePolicy, QWidget


class SceneItemDetailWidget(QWidget):
    """:class:`~nodedge.scene_item_detail_widget.SceneItemDetailWidget` class ."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout: QGridLayout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setAutoFillBackground(True)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

        # pal = QPalette()
        # pal.setColor(QPalette.Background, QColor("black"))
        # self.setPalette(pal)
        self.setLayout(self.layout)
        self.titleLineEdit: QLineEdit = self.addRow("Name", edit=True)
        self.titleLineEdit.editingFinished.connect(self.onTitleLineEditChanged)
        self.typeLabel = self.addRow("Type")
        self.inputsTypeLabel = self.addRow("Inputs type")
        self.outputsTypeLabel = self.addRow("Outputs type")

    def addRow(self, title: str, edit: bool = False):
        stringLabel = QLabel(title + ": ")
        stringLabel.setAlignment(Qt.AlignTop)
        stringLabel.setFixedHeight(30)

        if edit is True:
            valueWidget: QWidget = QLineEdit("")
        else:
            valueWidget = QLabel("")

        valueWidget.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        )
        valueWidget.setAlignment(Qt.AlignTop)
        valueWidget.setFixedHeight(30)

        rowCount = self.layout.rowCount()
        self.layout.addWidget(stringLabel, rowCount, 0)
        self.layout.addWidget(valueWidget, rowCount, 1)

        return valueWidget

    def update(self):
        super().update()

        if self.parent.currentEditorWidget is not None:
            selectedNode = self.parent.currentEditorWidget.scene.selectedNode
            if selectedNode is not None:
                self.titleLineEdit.setText(selectedNode.title)
                self.typeLabel.setText(selectedNode.graphicsNode.type)
                inputs = [i.name for i in selectedNode.inputSocketTypes]
                outputs = [i.name for i in selectedNode.outputSocketTypes]
                self.inputsTypeLabel.setText(str(inputs))
                self.outputsTypeLabel.setText(str(outputs))

    def onTitleLineEditChanged(self):
        selectedNode = self.parent.currentEditorWidget.scene.selectedNode

        otherNodes = self.parent.currentEditorWidget.scene.nodes.copy()
        if selectedNode in otherNodes:
            otherNodes.remove(selectedNode)

        alreadyExistingNames = [node.title for node in otherNodes]
        newTitle = self.titleLineEdit.text()
        self.__logger.debug(f"{newTitle}")
        self.__logger.debug(f"{alreadyExistingNames}")
        while newTitle in alreadyExistingNames:
            if newTitle[-1].isnumeric():
                newLastCharacter = str(int(newTitle[-1]) + 1)
                newTitle = newTitle[:-1]
                newTitle += newLastCharacter
            else:
                newTitle += "1"

        self.titleLineEdit.setText(newTitle)
        selectedNode.title = newTitle
