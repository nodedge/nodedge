import json
import logging
import os
import sys
from typing import Callable, List, Optional, Union

import pyqtgraph as pg
from asammdf import MDF
from asammdf.blocks.utils import MdfException
from asammdf.blocks.v2_v3_blocks import Channel
from pyqtgraph import PlotDataItem
from PySide6.QtCore import QSettings, QStandardPaths, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from nodedge.dats.curve_dialog import CurveDialog
from nodedge.dats.formula_evaluator import evaluateFormula
from nodedge.dats.logs_widget import LogsWidget
from nodedge.dats.n_plot_data_item import NPlotDataItem
from nodedge.dats.signals_widget import SignalsWidget
from nodedge.dats.workbooks_tab_widget import WorkbooksTabWidget
from nodedge.dats.worksheets_tab_widget import WorksheetsTabWidget
from nodedge.home_menu import MenuBar
from nodedge.logger import setupLogging
from nodedge.range_slider import RangeSlider
from nodedge.utils import dumpException

logger = logging.getLogger(__name__)


class DatsWindow(QMainWindow):
    recentFilesUpdated = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.companyName = "Nodedge"
        self.productName = "Dats"

        self.recentFiles: List[str] = []
        self.curveConfig = {}

        self.workbooksTabWidget = WorkbooksTabWidget(self)
        self.mainWidget = QWidget()
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.slider = RangeSlider(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.NoTicks)
        self.mainLayout.addWidget(self.workbooksTabWidget)
        self.mainLayout.addWidget(self.slider)
        self.slider.sliderMoved.connect(self.updatePlotAxes)
        self.workbooksTabWidget.workbooks[0].worksheets[0].xRangeUpdated.connect(
            self.updateSlider
        )
        self.setCentralWidget(self.mainWidget)

        self.signalsWidget = SignalsWidget(self)
        self.signalsDock = QDockWidget("Variables")
        self.signalsDock.setWidget(self.signalsWidget)
        self.signalsDock.setWidget(self.signalsWidget)
        self.signalsWidget.plotSelectedSignals.connect(self.onPlotSelectedItems)
        self.signalsWidget.signalsTableWidget.itemClicked.connect(
            self.onSignalTableItemClicked
        )

        self.logsWidget = LogsWidget()
        self.logsDock = QDockWidget("Data files")
        self.logsDock.setMinimumWidth(300)
        self.logsDock.setWidget(self.logsWidget)
        self.logsWidget.openButton.clicked.connect(self.openLog)
        self.logsWidget.logsListWidget.logSelected.connect(self.updateDataItems)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.logsDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.signalsDock)
        self.readSettings()
        self.createActions()
        self.createMenus()

        self.statusBar().showMessage("Welcome in Dats", timeout=5000)
        self.statusBar().show()

        self._configPath = ""
        self.createStatusBar()

        self._modifiedConfig = False

    @property
    def modifiedConfig(self):
        return self._modifiedConfig

    @modifiedConfig.setter
    def modifiedConfig(self, value):
        if value != self._modifiedConfig:
            self._modifiedConfig = value
            self.setConfigPathLabelText()

    def setConfigPathLabelText(self):
        text = "Configuration: "

        if not self.configPath:
            text += "untitled"
        else:
            text += self.configPath

        if self.modifiedConfig:
            text += "*"

        self.configPathLabel.setText(text)

    @property
    def configPath(self):
        return self._configPath

    @configPath.setter
    def configPath(self, path):
        self._configPath = path
        self.setConfigPathLabelText()

    def onSignalTableItemClicked(self, item):
        print(item.text())
        if item.text() in self.curveConfig:
            self.modifySignalAct.setEnabled(True)
        else:
            self.modifySignalAct.setEnabled(False)

    def createStatusBar(self) -> None:
        """
        Create Status bar and connect to
        :class:`~nodedge.graphics_view.GraphicsView`'s scenePosChanged event.
        """
        self.statusBar().showMessage("")
        self.configPathLabel = QLabel("Configuration: " + self.configPath)
        self.statusBar().addPermanentWidget(self.configPathLabel)

    def updatePlotAxes(self, low, high):
        if len(self.workbooksTabWidget.workbooks) == 0:
            return
        if len(self.workbooksTabWidget.workbooks[0].worksheets) == 0:
            return
        try:
            self.workbooksTabWidget.workbooks[0].worksheets[0].xRangeUpdated.disconnect(
                self.updateSlider
            )
        except RuntimeError as e:
            logger.warning(e)
        self.workbooksTabWidget.updateXAxis(low, high)
        self.workbooksTabWidget.workbooks[0].worksheets[0].xRangeUpdated.connect(
            self.updateSlider
        )

    def updateSlider(self, low, high):
        self.slider.sliderMoved.disconnect(self.updatePlotAxes)
        self.slider.setRange(low, high)
        self.slider.sliderMoved.connect(self.updatePlotAxes)

    def maybeSave(self) -> bool:
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
                return True
            elif res == QMessageBox.StandardButton.Discard:
                self.modifiedConfig = False
                return True
            elif res == QMessageBox.StandardButton.Cancel:
                return False
            else:
                return True
        return True

    def closeEvent(self, event: QCloseEvent) -> None:
        self.writeSettings()

        ret = self.maybeSave()

        if ret:
            event.accept()
        else:
            event.ignore()

    def saveConfiguration(self):
        layoutConfig = {}
        for workbook in self.workbooksTabWidget.workbooks:
            worksheet_config = {}
            for worksheet in workbook.worksheets:
                worksheet_config.update(worksheet.as_dict())
            layoutConfig.update({workbook.name: worksheet_config})

        config = {"layout": layoutConfig, "curves": self.curveConfig}

        if self.configPath == "":
            filename, _ = QFileDialog.getSaveFileName(
                parent=self,
                caption="Save config to file",
                dir=DatsWindow.getFileDialogDirectory(),
                filter="*.json",
            )
            if filename:
                self.configPath = filename
            else:
                return

        parsed = json.dumps(config, indent=2, sort_keys=True)
        with open(self.configPath, "w") as outfile:
            outfile.write(parsed)
        self.modifiedConfig = False

    def restoreConfiguration(self):
        filename, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="Restore configuration",
            dir=DatsWindow.getFileDialogDirectory(),
            filter="All files (*)",
        )

        self.configPath = filename

        if "json" not in filename:
            return

        with open(filename) as f:
            config = json.load(f)

        layoutConfig = config["layout"]

        self.workbooksTabWidget.clear()
        # self.workbooksTabWidget.removeWorkbook(0)
        for workbookname, workbookConfig in layoutConfig.items():
            worksheetsTabWidget = self.workbooksTabWidget.addWorkbook(workbookname)
            worksheetsTabWidget.removeWorksheet(0)
            item = 0
            for worksheetname, worksheetConfig in workbookConfig.items():
                worksheetsTabWidget.addWorksheet(worksheetname)
                worksheetsTabWidget.setCurrentIndex(item)
                logger.debug(f"Selecting worksheet: {item}")
                worksheet = worksheetsTabWidget.worksheets[item]
                for index, vbConfig in enumerate(worksheetConfig):
                    if index >= 1:
                        worksheet.plotItem.vb.addSubPlot()

                    for signalName, curveOptions in vbConfig.items():
                        dataItem: PlotDataItem = NPlotDataItem(
                            clickable=True,
                            pen=curveOptions,
                            skipFiniteCheck=True,
                            symbolPen=curveOptions,
                            symbol=None,
                        )

                        if self.logsWidget.logsListWidget.logs:
                            # logItem = self.logsWidget.logsListWidget.currentItem()
                            # log = self.logsWidget.logsListWidget.logs[logItem.text()]
                            logger.debug(f"Signal {signalName} is being restored")
                            self.plotCurves([signalName])
                        else:
                            dataItem.setData(
                                x=[0, 1],
                                y=[0, 0],
                                name=signalName,
                            )
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

    def closeConfiguration(self):
        self.maybeSave()
        self.modifiedConfig = False
        self.configPath = ""
        for index, workbook in enumerate(self.workbooksTabWidget.workbooks):
            self.workbooksTabWidget.removeWorkbook(index)

        self.workbooksTabWidget.addWorkbook()

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

        w: WorksheetsTabWidget = self.workbooksTabWidget.currentWidget()

        for name in channelNames:
            if name in list(w.currentWidget().plotItem.vb.curves.keys()):
                continue

            try:
                channel: Channel = log.get(name)
            except Exception as e:
                channelIndex, channelGroup = log.channels_db[name][0]
                channel: Channel = log.get(name, channelIndex, channelGroup)

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
            "Show information about Nodedge",
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

        self.closeConfigAct = self.createAction(
            "&Close configuration",
            self.closeConfiguration,
            "Close plots configuration",
            QKeySequence("Ctrl+Shift+R"),
        )

        self.addWorksheetAct = self.createAction(
            "&Add worksheet",
            self.addWorksheet,
            "Add worksheet",
            QKeySequence("Ctrl+T"),
        )

        self.addWorkbookAct = self.createAction(
            "&Add workbook",
            self.addWorkbook,
            "Add workbook",
            QKeySequence("Ctrl+Shift+T"),
        )

        self.removeWorksheetAct = self.createAction(
            "&Remove worksheet",
            self.removeWorksheet,
            "Remove worksheet",
            QKeySequence("Ctrl+W"),
        )

        self.removeWorkbookAct = self.createAction(
            "&Remove workbook",
            self.removeWorkbook,
            "Remove workbook",
            QKeySequence("Ctrl+Shift+W"),
        )

        self.addSubPlotAct = self.createAction(
            "&Add subplot",
            self.addSubPlot,
            "Add subplot",
            QKeySequence("Ctrl+Shift+P"),
        )

        self.closeSubPlotAct = self.createAction(
            "&Close subplot",
            self.closeSubPlot,
            "Close subplot",
            QKeySequence("Ctrl+Alt+P"),
        )

        self.delAct = self.createAction(
            "&Delete curve",
            self.deleteCurve,
            "Delete highlighted curve or last curve",
            QKeySequence("Del"),
        )

        self.createSignalAct = self.createAction(
            "&Create variable",
            self.createSignal,
            "Create variable",
            QKeySequence("Ctrl+M"),
        )

        self.modifySignalAct = self.createAction(
            "&Modify variable",
            self.modifySignal,
            "Modify variable",
            QKeySequence("Ctrl+Shift+M"),
        )
        self.modifySignalAct.setEnabled(False)

        self.FitToViewAct = self.createAction(
            "&Fit to view",
            self.viewAll,
            "Fit to view",
            QKeySequence("Space"),
        )

        self.takeScreenshotAct = self.createAction(
            "Take screenshot",
            self.onScreenshot,
            "Take screenshot",
            QKeySequence("Ctrl+Shift+Space"),
        )

        self.closeLogAct = self.createAction(
            "Close data file",
            self.closeLog,
            "Close data file",
            QKeySequence("Ctrl+Shift+Delete"),
        )

        self.helpAct = self.createAction(
            "&Help", self.onHelp, "Help", QKeySequence("F1")
        )

    def onHelp(self):
        pass

    def addSubPlot(self):
        worksheet = self.workbooksTabWidget.currentWidget()
        if not worksheet:
            return
        nPlotWidget = worksheet.currentWidget()
        if not nPlotWidget:
            return
        nPlotWidget.plotItem.vb.addSubPlot()

    def closeSubPlot(self):
        worksheet = self.workbooksTabWidget.currentWidget()
        if not worksheet:
            return
        nPlotWidget = worksheet.currentWidget()
        if not nPlotWidget:
            return
        nPlotWidget.plotItem.vb.closeCurrentSubPlot()

    def closeLog(self):
        for item in self.logsWidget.logsListWidget.selectedItems():
            self.logsWidget.logsListWidget.logs.pop(item.text())
            self.logsWidget.logsListWidget.takeItem(
                self.logsWidget.logsListWidget.row(item)
            )
            logger.debug(self.logsWidget.logsListWidget.selectedItems())

        self.updateDataItems(MDF())

    def onScreenshot(self):
        """
        Take screenshot
        """
        filename, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save graph to file",
            dir=DatsWindow.getFileDialogDirectory(),
            filter="PNG (*.png);; JPG (*.jpg);; JPEG (*.jpeg)",
        )

        if not filename:
            return

        self.workbooksTabWidget.currentWidget().grab().save(filename)

    def viewAll(self):
        w: WorksheetsTabWidget = self.workbooksTabWidget.currentWidget()
        w.viewAll()

    def createSignal(self):
        w: CurveDialog = CurveDialog(self)
        w.show()
        self.modifiedConfig = True

    def modifySignal(self):
        curveName = self.signalsWidget.signalsTableWidget.selectedItems()[0].text()
        curveConfig = self.curveConfig[curveName]
        w: CurveDialog = CurveDialog(self, curveName, curveConfig)
        w.show()
        log = self.logsWidget.logsListWidget.logs[
            self.logsWidget.logsListWidget.currentItem().text()
        ]
        self.signalsWidget.signalsTableWidget.updateItems(log)
        self.modifiedConfig = True

    def replaceCurve(self, oldName, newName):
        for workbook in self.workbooksTabWidget.workbooks:
            for worksheet in workbook.worksheets:
                for plotItem in worksheet.plotItems:
                    if oldName in list(plotItem.vb.curves.keys()):
                        curve = plotItem.vb.curves.pop(oldName)
                        plotItem.removeItem(curve)
                        self.workbooksTabWidget.setCurrentWidget(workbook)
                        workbook.setCurrentWidget(worksheet)
                        self.plotCurves([newName])

    def deleteCurve(self):

        worksheetTabWidget = self.workbooksTabWidget.currentWidget()
        nPlotWidget = worksheetTabWidget.currentWidget()
        if not nPlotWidget.items:
            return

        if nPlotWidget.plotItem.vb.highlightedCurve is not None:
            nPlotWidget.plotItem.vb.curves.pop(
                nPlotWidget.plotItem.vb.highlightedCurve.name()
            )
            nPlotWidget.plotItem.removeItem(nPlotWidget.plotItem.vb.highlightedCurve)
        else:
            lastKey = list(nPlotWidget.plotItem.vb.curves.keys())[-1]
            curve = nPlotWidget.plotItem.vb.curves.pop(lastKey)
            nPlotWidget.plotItem.removeItem(curve)
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
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)
        self.homeMenu = self.menubar.homeMenu
        self.homeMenu.aboutToShow.connect(self.closeHomeMenu)
        self.createFileMenu()
        self.createViewMenu()
        self.createToolsMenu()
        self.createHelpMenu()

    def createViewMenu(self):
        self.viewMenu: QMenu = self.menuBar().addMenu("&View")
        self.viewMenu.addAction(self.FitToViewAct)
        self.viewMenu.addSeparator()

    def closeHomeMenu(self):
        timer = QTimer(self)
        timer.singleShot(1, self.homeMenu.hide)

    def createToolsMenu(self):
        self.toolsMenu: QMenu = self.menuBar().addMenu("&Tools")
        self.toolsMenu.addAction(self.delAct)
        self.toolsMenu.addAction(self.createSignalAct)
        self.toolsMenu.addAction(self.modifySignalAct)

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createFileMenu(self):
        self.fileMenu: QMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.openAct)
        self.recentFilesMenu = self.fileMenu.addMenu("Open recent")
        self.updateRecentFilesMenu()
        self.fileMenu.addAction(self.closeLogAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.addWorkbookAct)
        self.fileMenu.addAction(self.removeWorkbookAct)
        self.fileMenu.addAction(self.addWorksheetAct)
        self.fileMenu.addAction(self.removeWorksheetAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.addSubPlotAct)
        self.fileMenu.addAction(self.closeSubPlotAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveConfigAct)
        self.fileMenu.addAction(self.restoreConfigAct)
        self.fileMenu.addAction(self.closeConfigAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.takeScreenshotAct)

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createHelpMenu(self):
        self.helpMenu: QMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.helpAct)

    def about(self) -> None:
        """
        About slot.

        Shows a message box with more information about Battery bench controller.

        :return: ``None``
        """
        QMessageBox.about(
            self,
            "About Nodedge",
            "Nodedge version: pre-release.\n\n"
            "For further information, please contact admin@nodedge.io.\n\n"
            "© 2020-2023 Nodedge",
        )

    def openLog(self, filename=None):
        if filename is None or not filename:
            filename, ok = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open data file",
                dir=DatsWindow.getFileDialogDirectory(),
                filter=DatsWindow.getFileDialogFilter(),
            )
            if not ok:
                return
        if not os.path.exists(filename):
            ok = QMessageBox.warning(
                self,
                "File not found",
                f"File {filename} does not exist. \n" "Do you want to open a new file?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            )
            self.removeFromRecentFiles(filename)
            if ok == QMessageBox.StandardButton.Ok:
                self.openLog()
            else:
                logger.warning(f"File {filename} not found.")
                return

        if os.path.isdir(filename):
            filename, ok = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open log example from file",
                dir=filename,
                filter=DatsWindow.getFileDialogFilter(),
            )

        log = self.logsWidget.logsListWidget.openLog(filename)
        self.updateDataItems(log)
        self.modifiedConfig = True

        self.addToRecentFiles(filename)
        if len(self.workbooksTabWidget.workbooks) == 0:
            self.addWorkbook()

    def addToRecentFiles(self, filepath):
        """
        Add to the recent files list.

        :param filepath: absolute path and filename of the file to open.
        :type filepath: ``str``
        """
        if filepath in self.recentFiles:
            self.recentFiles.remove(filepath)
        self.recentFiles.insert(0, filepath)

        if len(self.recentFiles) > 10:
            self.recentFiles.pop()

        self.writeRecentFilesSettings()
        self.updateRecentFilesMenu()

        self.recentFilesUpdated.emit(self.recentFiles)

    def removeFromRecentFiles(self, filePath: str):
        """
        Remove from the recent files list.

        :param filePath: absolute path and filename of the file to open.
        :type filePath: ``str``
        """
        if filePath in self.recentFiles:
            self.recentFiles.remove(filePath)

        self.writeRecentFilesSettings()
        self.updateRecentFilesMenu()

        self.recentFilesUpdated.emit(self.recentFiles)

    def updateRecentFilesMenu(self):
        self.recentFilesMenu.clear()
        logger.debug(f"Recent files: {self.recentFiles}")
        for index, filePath in enumerate(self.recentFiles):
            if index > 9:
                break

            shortpath = filePath.replace("\\", "/")
            shortpath = filePath.split("/")[-1]
            action = self.createAction(
                shortpath,
                lambda: self.openLog(filePath),
                f"Open {filePath}",
                QKeySequence(f"Ctrl+Shift+{index}"),
            )
            self.recentFilesMenu.addAction(action)

    def updateDataItems(self, log: Optional[MDF]):
        self.signalsWidget.signalsTableWidget.updateItems(log)

        if log is not None:
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
        lastFoundDataItem = NPlotDataItem()
        lastFoundDataItem.setData(x=[0, 1], y=[0, 1])
        for workbook in self.workbooksTabWidget.workbooks:
            for worksheet in workbook.worksheets:
                signalName: str
                dataItem: NPlotDataItem
                for signalName, dataItem in worksheet.items.items():
                    try:
                        data = log.get(signalName)
                        dataItem.show()
                        # dataItem.curve.show()
                        # dataItem.scatter.show()
                        dataItem.setData(
                            x=data.timestamps, y=data.samples, name=data.name
                        )
                        worksheet.updateRange(dataItem)
                        lastFoundDataItem = dataItem

                    except (MdfException, AttributeError) as e:
                        logging.warning(e)
                        dataItem.setData(x=[0, 1], y=[0, 0])
                        # worksheet.updateRange(dataItem)

                        # dataItem.curve.hide()
                        # dataItem.scatter.hide()
                        dataItem.hide()
                        # self.viewAll()

                worksheet.updateRange(lastFoundDataItem)
        # self.viewAll()

    @staticmethod
    def getFileDialogFilter() -> str:
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "All files (*);;MF4 (*.mf4);;CSV (*.csv);;HDF5 (*.hdf5)"

    def addWorksheet(self):
        if len(self.workbooksTabWidget.workbooks) == 0:
            self.workbooksTabWidget.addWorkbook()
        else:
            self.workbooksTabWidget.currentWidget().addWorksheet(True)
        self.modifiedConfig = True

    def addWorkbook(self):
        self.workbooksTabWidget.addWorkbook(True)
        self.modifiedConfig = True

    def removeWorkbook(self):
        if len(self.workbooksTabWidget.workbooks) > 0:
            self.workbooksTabWidget.removeWorkbook()
            self.modifiedConfig = True

    def removeWorksheet(self):
        if len(self.workbooksTabWidget.workbooks) > 0:
            self.workbooksTabWidget.currentWidget().removeWorksheet()
            self.modifiedConfig = True

    # def convertLogAndOpen(self):
    #     d = QFileDialog()
    #     files, _ = d.getOpenFileNames(None, "Choose files to convert", NPlotWindow.getFileDialogDirectory(), "*.csv")
    #     for file in files:
    #         csv_converter = CsvToMF4Converter(file, file)
    #         logName = csv_converter.convert()
    #
    #         self.openLog(logName)

    @staticmethod
    def getFileDialogDirectory() -> str:
        """
        Returns starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        settings = QSettings("Nodedge", "Nodedge")

        defaultWorkspacePath = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation
        )
        workspacePath = str(settings.value("workspacePath", defaultWorkspacePath))
        return workspacePath

    def readSettings(self):
        settings = QSettings(self.companyName, self.productName)
        self.recentFiles = list(settings.value("recent_files", []))

    def writeSettings(self):
        self.writeRecentFilesSettings()

    def writeRecentFilesSettings(self):
        """
        Write the recent files settings for this application.
        """
        settings = QSettings(self.companyName, self.productName)
        settings.setValue("recent_files", self.recentFiles)


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
