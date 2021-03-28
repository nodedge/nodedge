# -*- coding: utf-8 -*-
"""
${FILE_NAME} module containing :class:`~nodedge.${FILE_NAME}.<ClassName>` class.
"""
import pyqtgraph as pg
from PySide2.QtWidgets import QVBoxLayout, QWidget

from tools.plotter.curve_item import CurveItem


class CurveContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph: pg.PlotWidget = pg.PlotWidget()
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.mainLayout.addWidget(self.graph)
        self.curveItem = CurveItem()
        self.graph.addItem(self.curveItem)

        self.graph.showGrid(x=True, y=True)
