import logging
from typing import Callable, List, Optional, Union

import pyqtgraph as pg
from PySide6.QtCore import QEvent
from PySide6.QtGui import QAction, QKeySequence, QMouseEvent, Qt
from PySide6.QtWidgets import QInputDialog, QMenu, QTabWidget

from nodedge.dats.n_plot_data_item import NPlotDataItem
from nodedge.dats.n_plot_widget import NPlotWidget

logger = logging.getLogger(__name__)


class WorksheetsTabWidget(QTabWidget):
    def __init__(self, parent=None, workbookName="Workbook1"):
        super().__init__(parent)
        self.workbookTabsWidget = parent
        self.worksheets: List[NPlotWidget] = []
        self.addWorksheet()
        self.name = workbookName

        self.setTabsClosable(True)
        self.setMovable(True)
        # noinspection PyUnresolvedReferences
        self.setElideMode(Qt.ElideRight)
        self.setUsesScrollButtons(True)

        self.tabBar = self.tabBar()
        self.tabBar.installEventFilter(self)
        self.clickedIndex = None

        self.tabBarDoubleClicked.connect(self.renameWorksheet)
        self.tabBarClicked.connect(self.onTabBarClicked)
        self.tabCloseRequested.connect(self.removeWorksheet)

        self.createActions()

    # noinspection DuplicatedCode
    def eventFilter(self, watched, event):
        if watched == self.tabBar:
            if event.type() == QEvent.MouseButtonPress:
                event: QMouseEvent
                if event.button() == Qt.RightButton:
                    self.openContextMenu(event.pos(), event.globalPos())

        return super().eventFilter(watched, event)

    def openContextMenu(self, pos, globalPos):
        self.clickedIndex = self.tabBar.tabAt(pos)

        menu = QMenu()
        menu.addAction(self.createAct)
        menu.addAction(self.renameWorksheetAct)
        menu.addAction(self.closeAct)

        menu.exec(globalPos)

    def onTabBarClicked(self, index: int):
        pass

    def addWorksheet(self, worksheetName="Worksheet1"):
        if isinstance(worksheetName, bool):
            dlg = QInputDialog(self)
            dlg.setWindowTitle("Enter new worksheet name")
            dlg.setLabelText("Name:")
            dlg.setInputMode(QInputDialog.TextInput)
            dlg.setLabelText("Worksheet name:")
            dlg.resize(500, 100)
            ok = dlg.exec_()
            worksheetName = dlg.textValue()

            if not ok:
                return

        if len(self.worksheets) > 0:
            viewRange = self.worksheets[0].plotItem.viewRange()
        plotWidget = NPlotWidget(parent=self, name=worksheetName)

        for index, worksheet in enumerate(self.worksheets):
            if index == 0:
                plotWidget.updateLimits(worksheet.xLimits, worksheet.yLimits)
                if len(self.worksheets) > 0:
                    plotWidget.plotItem.setRange(xRange=viewRange[0])
            worksheet.plotItem.setXLink(plotWidget.plotItem)
        self.addTab(plotWidget, worksheetName)
        self.worksheets.append(plotWidget)

    def removeWorksheet(self, index=None):
        if index is None:
            if self.clickedIndex is not None:
                index = self.clickedIndex
            else:
                index = self.currentIndex()
        self.removeTab(index)
        self.worksheets.pop(index)

    def renameWorksheet(self, index=None, name=None):
        if index is None:
            index = self.clickedIndex
        if name is None:
            dlg = QInputDialog(self)
            dlg.setWindowTitle("Enter new worksheet name")
            dlg.setLabelText("Name:")
            dlg.setInputMode(QInputDialog.TextInput)
            dlg.setLabelText("Worksheet name:")
            logger.info(f"{name=}")
            dlg.resize(500, 100)
            ok = dlg.exec_()

            if not ok:
                return
            name = dlg.textValue()
        self.setTabText(index, name)
        self.worksheets[index].name = name

    # noinspection PyAttributeOutsideInit
    def createActions(self):
        self.createAct = self.createAction(
            "&Add worksheet",
            self.addWorksheet,
            "Add worksheet",
        )

        self.closeAct = self.createAction(
            "&Close",
            self.removeWorksheet,
            "Close worksheet",
        )

        self.renameWorksheetAct = self.createAction(
            "&Rename",
            self.renameWorksheet,
            "rename worksheet",
            QKeySequence("F2"),
        )

    # TODO: Remove duplicate of createAction method
    def createAction(
        self,
        name: str,
        callback: Callable,
        statusTip: Optional[str] = None,
        shortcut: Union[None, str, QKeySequence] = None,
    ) -> QAction:
        """
        Create an action for this window and add it to actions list.
        :param name: action's name
        :type name: ``str``
        :param callback: function to be called when the action is triggered
        :type callback: ``Callable``
        :param statusTip: Description of the action displayed
            at the bottom left of the application.
        :type statusTip: Optional[``str``]
        :param shortcut: Keyboard shortcut to trigger the action.
        :type shortcut: ``Optional[str]``
        :return:
        """
        act = QAction(name, self)
        act.triggered.connect(callback)  # type: ignore

        if statusTip is not None:
            act.setStatusTip(statusTip)
            act.setToolTip(statusTip)

        if shortcut is not None:
            act.setShortcut(QKeySequence(shortcut))

        self.addAction(act)

        return act

    def addCurvePlot(self, x, y, name=""):
        index = self.currentIndex()
        plotWidget: NPlotWidget = self.worksheets[index]
        colorIndex = len(plotWidget.plotItem.vb.curves.keys())
        dataItem: NPlotDataItem = NPlotDataItem(
            clickable=True,
            pen=({"color": (colorIndex, 13), "width": 2}),
            skipFiniteCheck=True,
            symbolPen=({"color": (colorIndex, 13), "width": 2}),
            symbol=None,
            symbolBrush=pg.intColor(colorIndex, 13),
        )

        dataItem.setData(x=x, y=y, name=name)
        plotWidget.addDataItem(dataItem, name)
        dataItem.getViewBox().setAutoPan(x=True, y=True)

        self.setTabToolTip(index, "\n".join(list(plotWidget.items.keys())))

    def viewAll(self):
        for worksheet in self.worksheets:
            worksheet.viewAll()
