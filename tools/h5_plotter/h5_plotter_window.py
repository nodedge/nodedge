# -*- coding: utf-8 -*-
"""
h5_plotter_window.py module containing :class:`~nodedge.h5_plotter_window.py.<ClassName>` class.
"""

import logging
import sys

import h5py
from PySide2.QtWidgets import QApplication, QFileDialog

from nodedge.utils import dumpException
from tools.main_window_template.main_window import MainWindow
from tools.main_window_template.mdi_area import MdiArea

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class H5PlotterWindow(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, applicationName="H5 Plotter")

        self.mdiArea = MdiArea()
        self.setCentralWidget(self.mdiArea)

    def openFile(self, filename: str = ""):
        logger.debug(filename)
        if filename in ["", None, False]:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open graph from file",
                dir=H5PlotterWindow.getFileDialogDirectory(),
                filter=H5PlotterWindow.getFileDialogFilter(),
            )

        self.loadCsv(filename)

    def loadH5File(self, fileName):
        raise NotImplementedError

    @staticmethod
    def getFileDialogDirectory() -> str:
        """
        Returns starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        return "../../log"

    @staticmethod
    def getFileDialogFilter() -> str:
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "Log (*.log);CSV (*.csv);All files (*)"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = H5PlotterWindow()
    window.showMaximized()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
