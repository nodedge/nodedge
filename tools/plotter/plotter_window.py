# -*- coding: utf-8 -*-
"""
plotter_window.py module containing :class:`~nodedge.plotter_window.py.<ClassName>` class.
"""

import logging
import sys

import h5py
import numpy as np
from h5py import Dataset, Group
from PySide2.QtCore import Qt
from PySide2.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QTreeWidget,
    QTreeWidgetItem,
)

from nodedge.utils import dumpException
from tools.main_window_template.main_window import MainWindow
from tools.main_window_template.mdi_area import MdiArea
from tools.plotter.curve_container import CurveContainer
from tools.plotter.utils import getAllH5Keys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class PlotterWindow(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, applicationName="Plotter")

        self.mdiArea = MdiArea()
        self.setCentralWidget(self.mdiArea)

        self.variableTree = QTreeWidget()
        self.variableTreeDock = QDockWidget("Variables")
        self.variableTreeDock.setWidget(self.variableTree)
        self.variableTreeDock.setFloating(False)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.variableTreeDock)

    def openFile(self, filename: str = ""):
        if filename in ["", None, False]:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open graph from file",
                dir=PlotterWindow.getFileDialogDirectory(),
                filter=PlotterWindow.getFileDialogFilter(),
            )

        extension = filename.split(".")[-1]
        if extension == "hdf5":
            file = self.loadHdf5(filename)
        elif extension == "csv":
            file = self.loadCsv(filename)
        else:
            return NotImplementedError

        # Get hdf5 key tree
        allKeys = getAllH5Keys(file)
        # Remove first key "/"
        allKeys = allKeys[1::]

        # Create QTreeWidgetItems and store them in a dictionary
        self.variableDict = {}
        for key in allKeys:
            itemTitle = key[1::].split("/")[-1]
            item = QTreeWidgetItem()
            item.setText(0, itemTitle)
            self.variableDict.update({key: item})

        # Populate the TreeWidget
        for key in self.variableDict.keys():
            # Keys always start with "/", so remove it
            splitKey = key[1::].split("/")
            # Case 1: Top level items
            if len(splitKey) == 1:
                self.variableTree.addTopLevelItem(self.variableDict[key])
            # Case 2: Child level items
            else:
                parentItemName = "/" + "/".join(splitKey[0:-1])
                parentItem = self.variableDict[parentItemName]
                parentItem.addChild(self.variableDict[key])

        # Select data to plot
        ax = 0
        agent = 0
        pos_k = np.array(file.get("sim_data/pos_k_i"))[ax, :, agent]

        widget = CurveContainer()
        widget.curveItem.setHDF5(pos_k)
        subWindow = self.mdiArea.addSubWindow(widget)
        subWindow.showMaximized()

        return file

    def loadCsv(self, filename):
        raise NotImplementedError

    def loadHdf5(self, filename):
        f = h5py.File(filename, "r")
        return f

    @staticmethod
    def getFileDialogDirectory() -> str:
        """
        Returns starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        return "../../data"

    @staticmethod
    def getFileDialogFilter() -> str:
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "HDF5 (*.hdf5);;CSV (*.csv);;All files (*)"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PlotterWindow()
    window.showMaximized()

    # Open file
    f = window.openFile()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
