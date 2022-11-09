import json
import logging
import sys
from typing import Callable, Optional, Union, cast

import pyqtgraph as pg
from asammdf import MDF
from asammdf.blocks.utils import MdfException
from asammdf.blocks.v2_v3_blocks import Channel
from pyqtgraph import PlotDataItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.dats.logs_widget import LogsWidget
from nodedge.dats.n_plot_data_item import NPlotDataItem
from nodedge.dats.n_plot_widget import NPlotWidget
from nodedge.dats.signals_widget import SignalsWidget
from nodedge.dats.workbooks_tab_widget import WorkbooksTabWidget
from nodedge.dats.worksheets_tab_widget import WorksheetsTabWidget
from nodedge.utils import dumpException


class DatsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.appStyler = ApplicationStyler()
        self.workbooksTabWidget = WorkbooksTabWidget(self)
        self.setCentralWidget(self.workbooksTabWidget)

        self.signalsWidget = SignalsWidget()
        self.signalsDock = QDockWidget("Signals")
        self.signalsDock.setWidget(self.signalsWidget)
        self.signalsDock.setWidget(self.signalsWidget)
        self.signalsWidget.plotSelectedSignals.connect(self.onPlotSelectedItems)

        self.logsWidget = LogsWidget()
        self.logsDock = QDockWidget("Logs")
        self.logsDock.setWidget(self.logsWidget)
        self.logsWidget.openButton.clicked.connect(self.openLog)
        self.logsWidget.logsListWidget.logSelected.connect(
            self.signalsWidget.signalsListWidget.updateList
        )
        self.logsWidget.logsListWidget.logSelected.connect(self.updateDataItems)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.signalsDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.logsDock)

        self.createActions()
        self.createMenus()

    def closeEvent(self, event: QCloseEvent) -> None:
        # pass
        self.saveConfiguration()

    def saveConfiguration(self):
        config = {}
        for workbook in self.workbooksTabWidget.workbooks:
            worksheet_config = {}
            for worksheet in workbook.worksheets:
                worksheet_config.update(worksheet.as_dict())
            config.update({workbook.name: worksheet_config})

        print(config)

        parsed = json.dumps(config, indent=2, sort_keys=True)
        with open("config.json", "w") as outfile:
            outfile.write(parsed)

    def restoreConfiguration(self):
        filename, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Restore configuration",
            dir=DatsWindow.getFileDialogDirectory(),
            filter="All files (*)",
        )

        if "json" not in filename:
            return

        with open(filename) as f:
            config = json.load(f)

        self.workbooksTabWidget.removeWorkbook(0)
        for workbookname, workbookConfig in config.items():
            worksheetsTabWidget = self.workbooksTabWidget.addWorkbook(workbookname)
            worksheetsTabWidget.removeWorksheet(0)
            index = 0
            for worksheetname, worksheetConfig in workbookConfig.items():
                worksheetsTabWidget.addWorksheet(worksheetname)
                worksheetsTabWidget.setCurrentIndex(index)
                worksheet = worksheetsTabWidget.worksheets[index]
                for vbConfig in worksheetConfig:
                    if len(worksheet.items) > 1:
                        worksheet.plotItem.vb.addSubPlot()
                    for signalName, curveOptions in vbConfig.items():
                        dataItem: PlotDataItem = NPlotDataItem(
                            clickable=True,
                            pen=curveOptions,
                            skipFiniteCheck=True,
                            symbolPen=curveOptions,
                            symbol=None,
                        )

                        dataItem.setData(x=[0, 0], y=[0, 0], name=signalName)
                        worksheet.addDataItem(dataItem, signalName)
                    index = index + 1

    def onPlotSelectedItems(self, items):
        channelNames = []
        for item in items:
            channelNames.append(item.text())

        self.plotCurves(channelNames)

    def plotCurves(self, channelNames):
        if not self.logsWidget.logsListWidget.selectedItems():
            return

        logName = self.logsWidget.logsListWidget.selectedItems()[0].text()

        log: MDF = self.logsWidget.logsListWidget.logs[logName]

        for name in channelNames:
            channel: Channel = log.get(name)
            w: WorksheetsTabWidget = self.workbooksTabWidget.currentWidget()
            w.addCurvePlot(channel.timestamps, channel.samples, channel.name)  # type: ignore

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createActions(self) -> None:
        """
        Create basic `File` and `Edit` actions.
        """

        self.openAct = self.createAction(
            "&Open",
            self.openLog,
            "Open a MF4 log",
            QKeySequence("Ctrl+O"),
        )

        self.aboutAct = self.createAction(
            "&About",
            self.about,
            "Show the application's About box",
            QKeySequence("Ctrl+H"),
        )

        self.saveConfigAct = self.createAction(
            "&Save configuration",
            self.saveConfiguration,
            "Save plots configuration",
            QKeySequence("Ctrl+S"),
        )

        self.restoreConfigAct = self.createAction(
            "&Restore configuration",
            self.restoreConfiguration,
            "Restore plots configuration",
            QKeySequence("Ctrl+R"),
        )

        self.createWorksheetAct = self.createAction(
            "&Create worksheet",
            self.createWorksheet,
            "Create worksheet",
            QKeySequence("Ctrl+N"),
        )

        self.createWorkbookAct = self.createAction(
            "&Create workbook",
            self.createWorkbook,
            "Create workbook",
            QKeySequence("Ctrl+Shift+N"),
        )

        self.delAct = self.createAction(
            "&Delete",
            self.deleteCurve,
            "Delete highlighted curve or last curve",
            QKeySequence("Del"),
        )

    def deleteCurve(self):

        worksheetTabWidget: WorksheetsTabWidget = cast(
            self.workbooksTabWidget.currentWidget(), WorksheetsTabWidget
        )
        nPlotWidget = cast(worksheetTabWidget.currentWidget(), NPlotWidget)
        if not nPlotWidget.items:
            return

        if nPlotWidget.highlightedCurve is not None:
            nPlotWidget.items.pop(nPlotWidget.highlightedCurve.name())
            nPlotWidget.removeItem(nPlotWidget.highlightedCurve)
        else:
            lastKey = list(nPlotWidget.items.keys())[-1]
            curve = nPlotWidget.items.pop(lastKey)
            nPlotWidget.removeItem(curve)

    # TODO: Remove duplicates of createAction
    # noinspection DuplicatedCode
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

    def createMenus(self):
        self.createFileMenu()
        self.createHelpMenu()

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createFileMenu(self):
        self.fileMenu: QMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.createWorksheetAct)
        self.fileMenu.addAction(self.createWorkbookAct)
        self.fileMenu.addAction(self.saveConfigAct)
        self.fileMenu.addAction(self.restoreConfigAct)

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createHelpMenu(self):
        self.helpMenu: QMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

    def about(self) -> None:
        """
        About slot.

        Shows a message box with more information about Battery bench controller.

        :return: ``None``
        """
        QMessageBox.about(
            self,
            "About Alpha analyzer",
            '"Your assumptions are your windows on the world. \n'
            "Scrub them off every once in a while, or the light won't come in.\" \n "
            "Isaac Asimov.",
        )

    def openLog(self, filename=None):
        if filename is None or filename is False:
            filename, ok = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open file",
                dir=DatsWindow.getFileDialogDirectory(),
                filter=DatsWindow.getFileDialogFilter(),
            )
            if not ok:
                return

        print(filename)
        log = self.logsWidget.logsListWidget.addLog(filename)
        self.updateDataItems(log)

    def updateDataItems(self, log):
        for workbook in self.workbooksTabWidget.workbooks:
            for worksheet in workbook.worksheets:
                signalName: str
                dataItem: NPlotDataItem
                for signalName, dataItem in worksheet.items.items():
                    try:
                        data = log.get(signalName)
                        dataItem.curve.show()
                        dataItem.scatter.show()
                        dataItem.setData(
                            x=data.timestamps, y=data.samples, name=data.name
                        )
                        worksheet.updateRange(dataItem)

                    except MdfException as mdfException:
                        logging.warning(mdfException)
                        dataItem.curve.hide()
                        dataItem.scatter.hide()

    @staticmethod
    def getFileDialogDirectory() -> str:
        """
        Returns starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        return "data"

    @staticmethod
    def getFileDialogFilter() -> str:
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "MF4 (*.mf4);;All files (*)"

    def createWorksheet(self):
        w: WorksheetsTabWidget = cast(
            self.workbooksTabWidget.currentWidget(), WorksheetsTabWidget
        )
        w.addWorksheet(True)

    def createWorkbook(self):
        self.workbooksTabWidget.addWorkbook(True)

    # def convertLogAndOpen(self):
    #     d = QFileDialog()
    #     files, _ = d.getOpenFileNames(None, "Choose files to convert", NPlotWindow.getFileDialogDirectory(), "*.csv")
    #     for file in files:
    #         csv_converter = CsvToMF4Converter(file, file)
    #         logName = csv_converter.convert()
    #
    #         self.openLog(logName)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setOrganizationName("Nodedge")
    app.setOrganizationDomain("nodedge.io")
    app.setApplicationName("Dats")
    pg.setConfigOption("background", app.palette().dark().color())  # type: ignore

    dats = DatsWindow()
    dats.showMaximized()
    # dats.logsWidget.logsListWidget.addLog("data/log.mf4")
    # dats.workbooksTabWidget.workbooks[0].renameWorksheet(0, "worksheetName")
    # dats.plotCurves(
    #     [
    #         "signal1",
    #         "signal2",
    #     ]
    # )
    # dats.workbooksTabWidget.workbooks[0].addWorksheet("worksheetName2")
    # dats.workbooksTabWidget.setCurrentIndex(1)
    # dats.plotCurves(
    #     [
    #         "signal3",
    #         "signal4",
    #     ]
    # )
    try:
        sys.exit(app.exec())
    except Exception as e:
        dumpException(e)
