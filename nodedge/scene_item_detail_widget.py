# -*- coding: utf-8 -*-
"""
Scene item detail widget module containing
:class:`~nodedge.scene_item_detail_widget.SceneItemDetailWidget` class.
"""
import logging
from typing import cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QSizePolicy, QWidget


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
        self.titleLineEdit: QLineEdit = cast(QLineEdit, self.addRow("Title", edit=True))
        self.titleLineEdit.setEnabled(False)
        self.titleLineEdit.editingFinished.connect(self.onTitleLineEditChanged)
        self.typeLabel: QLabel = cast(QLabel, self.addRow("Type"))
        self.inputsTypeLabel = cast(QLabel, self.addRow("Inputs type"))
        self.outputsTypeLabel = cast(QLabel, self.addRow("Outputs type"))

    def addRow(self, title: str, edit: bool = False):
        """
        Add a widget on a new row to the layout.

        :param title: Name of the row
        :param edit: Whether is it as `QLineEdit` or not.
        :return: added widget
        """
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
        # valueWidget.setAlignment(Qt.AlignTop)
        valueWidget.setFixedHeight(30)

        rowCount = self.layout.rowCount()
        self.layout.addWidget(stringLabel, rowCount, 0)
        self.layout.addWidget(valueWidget, rowCount, 1)

        return valueWidget

    def update(self) -> None:  # type: ignore
        """


        :return: `None`
        """
        super().update()

        self.titleLineEdit.setEnabled(False)

        if self.parent.currentEditorWidget is not None:
            selectedNode = self.parent.currentEditorWidget.scene.selectedNode
            self.__logger.debug(selectedNode)
            if selectedNode is not None:
                self.titleLineEdit.setEnabled(True)
                self.titleLineEdit.setText(selectedNode.title)
                self.typeLabel.setText(selectedNode.graphicsNode.type)
                inputs = [i.name for i in selectedNode.inputSocketTypes]
                outputs = [i.name for i in selectedNode.outputSocketTypes]
                self.inputsTypeLabel.setText(str(inputs))
                self.outputsTypeLabel.setText(str(outputs))
            else:
                self.titleLineEdit.setText("")
                self.typeLabel.setText("")
                self.inputsTypeLabel.setText("")
                self.outputsTypeLabel.setText("")

    def onTitleLineEditChanged(self) -> None:
        """
        Give a unique name to the selected node.

        :return: `None`
        """
        scene = self.parent.currentEditorWidget.scene  # type: ignore
        selectedNode = scene.selectedNode

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
