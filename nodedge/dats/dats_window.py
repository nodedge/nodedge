import json
import logging
import sys
from typing import Callable, Optional, Union, cast

import pyqtgraph as pg
from asammdf import MDF
from asammdf.blocks.utils import MdfException
from asammdf.blocks.v2_v3_blocks import Channel
from pyqtgraph import PlotDataItem
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMenu,
    QMessageBox,
)

from nodedge.dats.curve_dialog import CurveDialog
from nodedge.dats.formula_evaluator import evaluateFormula
from nodedge.dats.logs_widget import LogsWidget
from nodedge.dats.n_plot_data_item import NPlotDataItem
from nodedge.dats.n_plot_widget import NPlotWidget
from nodedge.dats.signals_widget import SignalsWidget
from nodedge.dats.workbooks_tab_widget import WorkbooksTabWidget
from nodedge.dats.worksheets_tab_widget import WorksheetsTabWidget
from nodedge.logger import setupLogging
from nodedge.utils import dumpException


class DatsWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.curveConfig = {}

        self.workbooksTabWidget = WorkbooksTabWidget(self)
        self.setCentralWidget(self.workbooksTabWidget)

        self.signalsWidget = SignalsWidget(self)
        self.signalsDock = QDockWidget("Signals")
        self.signalsDock.setWidget(self.signalsWidget)
        self.signalsDock.setWidget(self.signalsWidget)
        self.signalsWidget.plotSelectedSignals.connect(self.onPlotSelectedItems)

        self.logsWidget = LogsWidget()
        self.logsDock = QDockWidget("Logs")
        self.logsDock.setMinimumWidth(300)
        self.logsDock.setWidget(self.logsWidget)
        self.logsWidget.openButton.clicked.connect(self.openLog)
        self.logsWidget.logsListWidget.logSelected.connect(self.updateDataItems)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.logsDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.signalsDock)

        self.createActions()
        self.createMenus()

        self.modifiedConfig = False

    def closeEvent(self, event: QCloseEvent) -> None:

        if self.modifiedConfig:
            res = QMessageBox.warning(
                self,
                "Dats is about to close",
                "There are unsaved modifications. \n"
                "Do you want to save your changes?",
                QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Discard
                | QMessageBox.StandardButton.Cancel,
            )

            if res == QMessageBox.StandardButton.Save:
                self.saveConfiguration()
                event.accept()
            elif res == QMessageBox.StandardButton.Cancel:
                event.ignore()
            else:
                event.accept()
        else:
            event.accept()

    def saveConfiguration(self):
        layoutConfig = {}
        for workbook in self.workbooksTabWidget.workbooks:
            worksheet_config = {}
            for worksheet in workbook.worksheets:
                worksheet_config.update(worksheet.as_dict())
            layoutConfig.update({workbook.name: worksheet_config})

        config = {"layout": layoutConfig, "curves": self.curveConfig}

        parsed = json.dumps(config, indent=2, sort_keys=True)
        with open("config.json", "w") as outfile:
            outfile.write(parsed)
        self.modifiedConfig = False

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

        layoutConfig = config["layout"]

        self.workbooksTabWidget.removeWorkbook(0)
        for workbookname, workbookConfig in layoutConfig.items():
            worksheetsTabWidget = self.workbooksTabWidget.addWorkbook(workbookname)
            worksheetsTabWidget.removeWorksheet(0)
            item = 0
            for worksheetname, worksheetConfig in workbookConfig.items():
                worksheetsTabWidget.addWorksheet(worksheetname)
                worksheetsTabWidget.setCurrentIndex(item)
                worksheet = worksheetsTabWidget.worksheets[item]
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
                    item = item + 1

        self.curveConfig = config["curves"]

        if self.logsWidget.logsListWidget.logs:
            item = self.logsWidget.logsListWidget.currentItem()
            log = self.logsWidget.logsListWidget.logs[item.text()]
            for curveName in self.curveConfig:
                formula = self.curveConfig[curveName]["formula"]
                signals = self.signalsWidget.signalsTableWidget.signals

                newSignal = evaluateFormula(curveName, formula, signals, log)

                log.append(newSignal)
            self.signalsWidget.signalsTableWidget.updateItems(log)

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
            try:
                channel: Channel = log.get(name)
            except Exception as e:
                channelIndex, channelGroup = log.channels_db[name][0]
                channel: Channel = log.get(name, channelIndex, channelGroup)

            w: WorksheetsTabWidget = self.workbooksTabWidget.currentWidget()
            w.addCurvePlot(channel.timestamps, channel.samples, channel.name)

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

        self.createCurveAct = self.createAction(
            "&Create curve",
            self.createCurve,
            "Create curve",
            QKeySequence("Ctrl+M"),
        )

        self.viewAllAct = self.createAction(
            "&View all",
            self.viewAll,
            "View all",
            QKeySequence("Space"),
        )

    def viewAll(self):
        w: WorksheetsTabWidget = self.workbooksTabWidget.currentWidget()
        w.viewAll()

    def createCurve(self):
        w: CurveDialog = CurveDialog(self)
        w.show()
        self.modifiedConfig = True

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
        self.modifiedConfig = True

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
        self.homeMenu: QMenu = self.menuBar().addMenu("&Home")
        self.homeMenu.aboutToShow.connect(self.closeHomeMenu)
        self.createFileMenu()
        self.createHelpMenu()
        self.createToolsMenu()

    def closeHomeMenu(self):
        timer = QTimer(self)
        timer.singleShot(1, self.homeMenu.hide)

    def createToolsMenu(self):
        self.toolsMenu: QMenu = self.menuBar().addMenu("&Tools")
        self.toolsMenu.addAction(self.delAct)
        self.toolsMenu.addAction(self.createCurveAct)

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

        log = self.logsWidget.logsListWidget.openLog(filename)
        self.updateDataItems(log)
        self.modifiedConfig = True

    def updateDataItems(self, log):
        self.signalsWidget.signalsTableWidget.updateItems(log)

        for curveName in self.curveConfig:
            formula = self.curveConfig[curveName]["formula"]
            signals = self.signalsWidget.signalsTableWidget.signals

            newSignal = evaluateFormula(curveName, formula, signals, log)

            if newSignal is None:
                ret = QMessageBox.warning(
                    self,
                    "Error",
                    f"Error evaluating formula for curve {curveName}.\n Do you want to continue computing curves?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )

                if ret == QMessageBox.StandardButton.No:
                    break
                elif ret == QMessageBox.StandardButton.Yes:
                    continue

            log.append(newSignal)
        self.signalsWidget.signalsTableWidget.updateItems(log)
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
        return "All files (*);;MF4 (*.mf4);;CSV (*.csv);;HDF5 (*.hdf5)"

    def createWorksheet(self):
        w: WorksheetsTabWidget = cast(
            self.workbooksTabWidget.currentWidget(), WorksheetsTabWidget
        )
        w.addWorksheet(True)
        self.modifiedConfig = True

    def createWorkbook(self):
        self.workbooksTabWidget.addWorkbook(True)
        self.modifiedConfig = True

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
    pg.setConfigOption("background", app.palette().dark().color())
    setupLogging()

    dats = DatsWindow()
    dats.showMaximized()
    # dats.logsWidget.logsListWidget.openLog("data/log.mf4")
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
