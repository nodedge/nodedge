# -*- coding: utf-8 -*-
import logging
import os
import random
import sys

import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotDataItem
from PySide2.QtCore import Qt, QTimer
from PySide2.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMdiArea,
    QVBoxLayout,
    QWidget,
)

from tools.main_window_template.application_styler import ApplicationStyler
from tools.plotter.time_axis_item import TimeAxisItem
from tools.plotter.utils import get_random_string, loadStyleSheets, timestamp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class MicroPlot(QWidget):
    def __init__(
        self, title: str = "", unit: str = "", simulatedData=False, parent=None
    ):
        super().__init__(parent)

        self.setAutoFillBackground(True)
        self.graph = pg.PlotWidget(
            axisItems={"bottom": TimeAxisItem(orientation="bottom")}
        )
        self.graph.hideAxis("bottom")
        self.graph.setMouseEnabled(False, False)
        # self.graph.hideAxis("left")
        # self.graph.setBackground("w")
        # self.graph.showGrid(x=True, y=True)
        self.graph.setDownsampling(mode="peak")
        # self.graph.setBackground("black")

        self.curveColor = QApplication.instance().palette().buttonText().color()
        self.curve: PlotDataItem = self.graph.plot(
            pen=pg.mkPen(self.curveColor, width=1)
        )
        self.data = np.ndarray(shape=(0, 2), dtype=float, order="F")
        # self.graph.setLabel("left", "Signal value")
        # self.graph.setLabel("bottom", "Time [s]")
        # self.graph.setXRange(timestamp(), timestamp() + 5)
        self.graph.setClipToView(True)
        self.setWindowTitle(title)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.setMargin(0)
        self.mainLayout.setSpacing(0)

        self.setLayout(self.mainLayout)

        self.mainLayout.addWidget(self.graph)

        self.labelContainer = QWidget()
        self.labelContainerLayout = QHBoxLayout()
        self.labelContainerLayout.setMargin(0)
        self.labelContainerLayout.setSpacing(0)

        self.labelContainer.setLayout(self.labelContainerLayout)
        self.mainLayout.addWidget(self.labelContainer)

        self.titleLabel = QLabel()
        self.titleLabel.setAlignment(Qt.AlignCenter)
        self.titleLabel.setText(title)
        self.titleLabel.setAutoFillBackground(True)
        self.labelContainerLayout.addWidget(self.titleLabel)
        self.valueLabel: QLabel = QLabel()
        self.valueLabel.setAlignment(Qt.AlignCenter)
        self.valueLabel.setAutoFillBackground(True)
        self.labelContainerLayout.addWidget(self.valueLabel)
        self.unitLabel = QLabel()
        self.unitLabel.setAlignment(Qt.AlignCenter)
        self.unitLabel.setText(unit)
        self.unitLabel.setAutoFillBackground(True)
        self.labelContainerLayout.addWidget(self.unitLabel)

        self.titleLabel.setAutoFillBackground(True)

        self.simulatedData = simulatedData
        if self.simulatedData:
            self.simulatorTimer = QTimer()
            self.simulatorTimer.timeout.connect(self.appendData)
            self.simulatorTimer.start(20)

    def appendData(self, value=None, time=None):
        if time is None:
            time = timestamp()
        if value is None:
            value = random.random()
            if self.simulatedData:
                self.simulatorTimer.start()
        if np.shape(self.data)[0] > 200:
            self.data = np.append(self.data[1::], [[time, value]], axis=0)
        else:
            self.data = np.append(self.data, [[time, value]], axis=0)

        self.curve.setData(self.data)
        self.valueLabel.setText(str(f"{value:.2f}"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()

    appStyler = ApplicationStyler()
    pg.setConfigOption("background", app.palette().dark())  # type: ignore
    # pg.setConfigOption("foreground", "w")
    styleSheetFilename = os.path.join(
        os.path.dirname(__file__), "qss/plotter_style.qss"
    )
    loadStyleSheets(styleSheetFilename)
    mdiArea = QMdiArea()
    window.setCentralWidget(mdiArea)
    boxLayout = QGridLayout()
    mdiArea.setLayout(boxLayout)
    widgets = []
    for i in range(10):
        for j in range(2):
            microPlot = MicroPlot(
                str(i) + str(j), get_random_string(3), simulatedData=True
            )
            widgets.append(microPlot)
            boxLayout.addWidget(microPlot, i, j)
    window.showMaximized()
    app.exec_()
