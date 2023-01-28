# -*- coding: utf-8 -*-
"""
Scene item detail widget module containing
:class:`~nodedge.scene_item_detail_widget.SceneItemDetailWidget` class.
"""
import copy
import logging
from typing import List, Optional, cast

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QSpinBox,
    QTextEdit,
    QWidget,
)

from nodedge import utils
from nodedge.blocks.block_param import BlockParam, BlockParamType

logger = logging.getLogger(__name__)


class SceneItemDetailWidget(QFrame):
    """:class:`~nodedge.scene_item_detail_widget.SceneItemDetailWidget` class ."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.layout: QGridLayout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.setAutoFillBackground(True)

        # pal = QPalette()
        # pal.setColor(QPalette.Background, QColor("black"))
        # self.setPalette(pal)
        self.setLayout(self.layout)
        self.titleLineEdit: QLineEdit = cast(
            QLineEdit, self.addRow("Title", shortEdit=True)
        )
        self.titleLineEdit.setEnabled(False)
        self.titleLineEdit.editingFinished.connect(self.onTitleLineEditChanged)
        self.typeLabel: QLabel = cast(QLabel, self.addRow("Type"))
        self.inputsTypeLabel = cast(QLabel, self.addRow("Inputs type"))
        self.outputsTypeLabel = cast(QLabel, self.addRow("Outputs type"))
        self.paramsFrame = QFrame()
        self.paramsFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.paramsLayout = QFormLayout()
        self.paramsFrame.setLayout(self.paramsLayout)
        self.addRow("Params", shortEdit=False, widget=self.paramsFrame)

        self.paramWidgets = {}

    def addRow(
        self, title: str, shortEdit: bool = False, widget: Optional[QWidget] = None
    ):
        """
        Add a widget on a new row to the layout.

        :param title: Name of the row
        :param shortEdit: Whether is it as `QLineEdit` or not.
        :return: added widget
        """
        stringLabel = QLabel(title + ": ")
        stringLabel.setAlignment(Qt.AlignTop)
        stringLabel.setFixedHeight(30)

        if shortEdit is True:
            valueWidget: QWidget = QLineEdit("")
            valueWidget.setFixedHeight(30)

        else:
            if widget is None:
                valueWidget = QLabel("")
                valueWidget.setFixedHeight(30)

            else:
                valueWidget = widget

        valueWidget.setSizePolicy(
            QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        )
        # valueWidget.setAlignment(Qt.AlignTop)

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
            logger.debug(selectedNode)
            if selectedNode is not None:
                self.titleLineEdit.setEnabled(True)
                self.titleLineEdit.setText(selectedNode.title)
                self.typeLabel.setText(selectedNode.graphicsNode.type)
                inputs = [i.name for i in selectedNode.inputSocketTypes]
                outputs = [i.name for i in selectedNode.outputSocketTypes]
                self.inputsTypeLabel.setText(str(inputs))
                self.outputsTypeLabel.setText(str(outputs))
                if hasattr(selectedNode, "params"):
                    self.updateParams(selectedNode.params)
            else:
                self.titleLineEdit.setText("")
                self.typeLabel.setText("")
                self.inputsTypeLabel.setText("")
                self.outputsTypeLabel.setText("")
                self.updateParams([])

    def updateParams(self, params: List[BlockParam]):
        """
        Update the params of the selected node.

        :param params: List of params
        :return: `None`
        """

        print([param.value for param in params])
        for i in reversed(range(self.paramsLayout.count())):
            self.paramsLayout.itemAt(i).widget().setParent(None)

        self.paramWidgets = {}

        for param in params:
            logger.debug(param.paramType)
            if param.paramType == BlockParamType.Int:
                spinbox = QSpinBox()
                spinbox.setValue(param.value)
                if param.minValue is not None:
                    spinbox.setMinimum(param.minValue)
                if param.maxValue is not None:
                    spinbox.setMaximum(param.maxValue)
                if param.step is not None:
                    spinbox.setSingleStep(param.step)
                self.paramsLayout.addRow(param.name, spinbox)
                self.paramWidgets.update({param.name: spinbox})
            elif param.paramType == BlockParamType.Float:
                doubleSpinbox: QDoubleSpinBox = QDoubleSpinBox()
                doubleSpinbox.setValue(param.value)
                if param.minValue is not None:
                    doubleSpinbox.setMinimum(param.minValue)
                if param.maxValue is not None:
                    doubleSpinbox.setMaximum(param.maxValue)
                if param.step is not None:
                    doubleSpinbox.setSingleStep(param.step)
                self.paramsLayout.addRow(param.name, doubleSpinbox)
                self.paramWidgets.update({param.name: doubleSpinbox})

            elif param.paramType == BlockParamType.ShortText:
                lineEdit = QLineEdit()
                lineEdit.setText(param.value)
                if param.maxValue is not None:
                    lineEdit.setMaxLength(param.maxValue)
                self.paramsLayout.addRow(param.name, lineEdit)
                self.paramWidgets.update({param.name: lineEdit})

            elif param.paramType == BlockParamType.LongText:
                textEdit = QTextEdit()
                textEdit.setText(param.value)
                self.paramsLayout.addRow(param.name, textEdit)
                self.paramWidgets.update({param.name: textEdit})

            elif param.paramType == BlockParamType.Bool:
                checkBox = QCheckBox()
                checkBox.setChecked(param.value)
                self.paramsLayout.addRow(param.name, checkBox)
                self.paramWidgets.update({param.name: checkBox})

            else:
                raise NotImplementedError(
                    f"Param type {param.paramType} not implemented"
                )

        for n, w in self.paramWidgets.items():
            if hasattr(w, "valueChanged"):
                w.valueChanged.connect(
                    lambda value, paramName=n: self.onParamWidgetChanged(
                        paramName, value
                    )
                )
            elif hasattr(w, "textChanged"):
                w.textChanged.connect(
                    lambda value, paramName=n: self.onParamWidgetChanged(
                        paramName, value
                    )
                )
            elif hasattr(w, "stateChanged"):
                w.stateChanged.connect(
                    lambda value, paramName=n: self.onParamWidgetChanged(
                        paramName, value
                    )
                )

    def onParamWidgetChanged(self, paramName: str, paramValue) -> None:
        scene = self.parent.currentEditorWidget.scene  # type: ignore
        selectedNode = scene.selectedNode

        print(f"paramName: {paramName}")
        print(f"paramValue: {paramValue}")

        try:
            for p in selectedNode.params:
                if p.name == paramName:
                    p.value = paramValue
                    break
        except KeyError:
            logger.error(f"Param {paramName} not found")
        except Exception as e:
            logger.error(e)

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

        alreadyExistingTitles = [node.title for node in otherNodes]
        newTitle = self.titleLineEdit.text()
        newTitle = utils.setNewTitle(newTitle, alreadyExistingTitles)

        self.titleLineEdit.setText(newTitle)
        selectedNode.title = newTitle
