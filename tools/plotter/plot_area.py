# -*- coding: utf-8 -*-
"""
plot_area.py module containing :class:`~nodedge.plot_area.py.<ClassName>` class.
"""
import sys

from pyqtgraph.dockarea import DockArea
from PySide2.QtGui import QCursor, QMouseEvent
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QInputDialog,
    QMainWindow,
    QMdiSubWindow,
    QVBoxLayout,
    QWidget,
)

from nodedge.utils import dumpException
from tools.main_window_template.mdi_area import MdiArea
from tools.plotter.range_slider_plot import RangeSliderPlot
from tools.plotter.worksheet_area import WorksheetArea


class PlotArea(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(800, 600)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.mdiArea = MdiArea(parent)
        self.workbooks = []
        self.subwindows = []
        self.addWorkbook("Untitled")

        self.layout.addWidget(self.mdiArea)

    def addWorkbook(self, workbookname=None):
        if workbookname is None or isinstance(workbookname, bool):
            nameDialog = QInputDialog()
            workbookname, okPressed = nameDialog.getText(
                self, "Workbook title", "Enter workbook's title below:"
            )

            if not okPressed:
                return

        dockArea = WorksheetArea()
        self.workbooks.append(dockArea)
        subwindow = self.mdiArea.addSubWindow(dockArea)
        subwindow.setWindowTitle(workbookname)
        subwindow.showMaximized()

        menu = subwindow.systemMenu()
        renameAction: QAction = QAction("Rename", menu)
        menu.addAction(renameAction)
        renameAction.triggered.connect(self.newName)
        newWorkBookAction: QAction = QAction("New workbook", menu)
        menu.addAction(newWorkBookAction)
        newWorkBookAction.triggered.connect(self.addWorkbook)

    def newName(self, trigger: bool):
        mousePos = QCursor.pos()
        subwindow = self.childAt(mousePos.x(), mousePos.y())
        # If a plot has already been drawn, the item at the cursor position is the
        # plot itself. To find the subwindow, iterate through its parents.
        while not isinstance(subwindow, QMdiSubWindow):
            subwindow = subwindow.parentWidget()

        nameDialog = QInputDialog()
        newTitle, okPressed = nameDialog.getText(
            self, "New title", "Enter new title below:"
        )

        if not okPressed:
            return

        subwindow.setWindowTitle(newTitle)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setCentralWidget(PlotArea())
    window.showMaximized()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
