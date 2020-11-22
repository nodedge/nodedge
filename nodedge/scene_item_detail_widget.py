# -*- coding: utf-8 -*-
"""
Scene item detail widget module containing
:class:`~nodedge.scene_item_detail_widget.SceneItemDetailWidget` class.
"""
from PySide2.QtCore import Qt
from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QGridLayout, QLabel, QSizePolicy, QWidget


class SceneItemDetailWidget(QWidget):
    """:class:`~nodedge.scene_item_detail_widget.SceneItemDetailWidget` class ."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setAutoFillBackground(True)
        # pal = QPalette()
        # pal.setColor(QPalette.Background, QColor("black"))
        # self.setPalette(pal)
        self.setLayout(self.layout)
        self.titleLabel = self.addRow("Name")
        self.typeLabel = self.addRow("Type")
        self.inputsTypeLabel = self.addRow("Inputs type")
        self.outputsTypeLabel = self.addRow("Outputs type")

    def addRow(self, title: str):
        stringLabel = QLabel(title + ": ")
        stringLabel.setAlignment(Qt.AlignTop)
        stringLabel.setFixedHeight(30)
        valueLabel = QLabel("")
        valueLabel.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        )
        valueLabel.setAlignment(Qt.AlignTop)
        valueLabel.setFixedHeight(30)

        rowCount = self.layout.rowCount()
        self.layout.addWidget(stringLabel, rowCount, 0)
        self.layout.addWidget(valueLabel, rowCount, 1)

        return valueLabel

    def update(self):
        super().update()

        if self.parent.currentEditorWidget is not None:
            selectedNode = self.parent.currentEditorWidget.scene.selectedNode
            if selectedNode is not None:
                self.titleLabel.setText(selectedNode.title)
                self.typeLabel.setText(selectedNode.graphicsNode.type)
                inputs = [i.name for i in selectedNode.inputSocketTypes]
                outputs = [i.name for i in selectedNode.outputSocketTypes]
                self.inputsTypeLabel.setText(str(inputs))
                self.outputsTypeLabel.setText(str(outputs))
