# -*- coding: utf-8 -*-
"""
plotter_window.py module containing :class:`~nodedge.plotter_window.py.<ClassName>` class.
"""
import json
import logging
import os
import sys
from enum import IntEnum
from typing import Optional

import h5py
import numpy as np
import pandas as pd
from PySide2.QtCore import QSize, Qt, Slot
from PySide2.QtGui import QKeySequence
from PySide2.QtWidgets import QApplication, QDockWidget, QFileDialog, QMdiSubWindow

from nodedge.utils import dumpException
from tools.main_window_template.main_window import MainWindow
from tools.plotter.countable_dock import CountableDock
from tools.plotter.plot_area import PlotArea
from tools.plotter.range_slider_plot import RangeSliderPlot
from tools.plotter.ranged_plot import RangedPlot
from tools.plotter.sized_input_dialog import SizedInputDialog
from tools.plotter.utils import convert, getAllKeysHdf5
from tools.plotter.variable_tree_widget import VariableTreeWidget
from tools.plotter.worksheet_area import WorksheetArea


class PlottingOption(IntEnum):
    ADD_NEW_WORKSHEET = 1  #:
    APPEND_IN_CURRENT_WORKSHEET = 2  #:
    ADD_NEW_WORKBOOK = 3  #:
    ADD_IN_GIVEN_WORKSHEET = 4


class PlotterWindow(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, applicationName="Plotter")

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)

        self.plotArea = PlotArea()
        self.setCentralWidget(self.plotArea)
        self.plotArea.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)

        # Make sure left and right docks have higher priority than top and bottom docks
        self.setCorner(Qt.BottomLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.TopLeftCorner, Qt.LeftDockWidgetArea)
        self.setCorner(Qt.BottomRightCorner, Qt.RightDockWidgetArea)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)

        self.variableTree = VariableTreeWidget()
        self.variableTree.variableDoubleClicked.connect(self.plotData)
        self.variableTree.variableCtrlClicked.connect(self.onVariableCtrlClicked)
        self.variableTree.variableShiftClicked.connect(self.onVariableShiftClicked)
        self.variableTreeDock = QDockWidget("Variables")
        self.variableTreeDock.setWidget(self.variableTree)
        self.variableTreeDock.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.variableTreeDock)

        self.rangeSliderPlot = RangeSliderPlot()
        self.rangeSliderDock = QDockWidget("Timeline")
        self.rangeSliderDock.setWidget(self.rangeSliderPlot)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.rangeSliderDock)

        self.workspaceName: str = ""

        self.file = None
        self.lastSelectedGraph: Optional[RangedPlot] = None

    def onSubWindowActivated(self, subwindow):
        self.__logger.debug(subwindow)
        # Reset last selected graph
        self.lastSelectedGraph = None

    @property
    def hasWorkspaceName(self):
        return self.workspaceName is not ""

    def openFile(self, filename: str = ""):
        self.variableTree.clear()
        # TODO: Clear all curves

        if filename in ["", None, False]:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open file",
                dir=PlotterWindow.getFileDialogDirectory(),
                filter=PlotterWindow.getFileDialogFilter(),
            )

        extension = filename.split(".")[-1]
        if extension == "hdf5" or extension == "h5" or extension == "he5":
            # Load hdf5 file
            self.file = self.loadHdf5(filename)

            # Get hdf5 key tree
            allKeys, allTypes, allVariableTypes = getAllKeysHdf5(self.file)
            self.variableTree.updateVariablesHdf5(allKeys, allTypes, allVariableTypes)

        elif extension == "csv":
            # Load csv file
            self.file = self.loadCsv(filename)

            # Get csv key tree
            allKeys = self.file.keys()
            self.variableTree.updateVariablesCsv(allKeys)
        else:
            return

        subWindowList = self.plotArea.mdiArea.subWindowList()
        for subWindow in subWindowList:
            keys = list(subWindow.widget().docks.data.keys())
            for k in keys:
                dock = subWindow.widget().docks[k]
                graph = dock.widgets[0]
                for curve in graph.curveNames:
                    self.plotData(
                        curve,
                        option=PlottingOption.ADD_IN_GIVEN_WORKSHEET,
                        worksheet=graph,
                    )

    def onVariableShiftClicked(self, variableName):
        self.plotData(variableName, option=PlottingOption.APPEND_IN_CURRENT_WORKSHEET)

    def onVariableCtrlClicked(self, variableName):
        self.plotData(variableName, option=PlottingOption.ADD_NEW_WORKBOOK)

    @Slot(str)  # type: ignore
    def plotData(
        self,
        variableName: str,
        option: PlottingOption = PlottingOption.ADD_NEW_WORKSHEET,
        indices=None,
        worksheet=None,
    ):

        if variableName[-1] == "]":
            fullVariableName = variableName
            variableName, indices = fullVariableName.split("[")
            indices = "[" + indices
        dataToBePlotted, fullDatasetName = self.selectDataToBePlotted(
            variableName, indices
        )

        # Find time
        dataPath = fullDatasetName.split("/")[0:-1]
        timeFullName = dataPath + ["time"]

        fullTimeSetName = "".join(timeFullName)
        timeSet = self.file[fullTimeSetName][:]

        if option in [
            PlottingOption.ADD_NEW_WORKBOOK,
            PlottingOption.ADD_NEW_WORKSHEET,
        ] or (
            option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET
            and self.lastSelectedGraph is None
        ):
            # Select current subwindow
            currentSubwindow = self.selectSubwindow(option)

            # Select dock where to plot
            dock = self.selectDock(currentSubwindow, option)
            dock.setTitle(fullDatasetName)
            worksheet = dock.widgets[0]
        elif option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET:
            worksheet = self.lastSelectedGraph

        worksheet.plotData(y=dataToBePlotted, x=timeSet)
        worksheet.selected.connect(self.onGraphSelected)
        self.rangeSliderPlot.linkPlot(worksheet)

    def onGraphSelected(self, graph):
        self.__logger.debug(f"Selected graph: {graph}")
        self.lastSelectedGraph = graph

    def selectDataToBePlotted(self, variableName, indices=None):
        # If no file has been opened yet, do nothing
        if self.file is None:
            if indices is not None:
                fullDatasetName = variableName + indices
            else:
                fullDatasetName = variableName
            return np.array([0]), fullDatasetName

        if isinstance(self.file, h5py.File):
            dataToBePlotted, fullDatasetName = self.extractDataFromHdf5(
                variableName, indices
            )
        elif isinstance(self.file, pd.core.frame.DataFrame):
            dataToBePlotted = np.array(self.file[variableName])
            fullDatasetName = variableName
        else:
            raise NotImplementedError
        return dataToBePlotted, fullDatasetName

    def selectDock(self, currentSubwindow, option, dock=None):
        keys = list(currentSubwindow.widget().docks.data.keys())
        if (
            option is PlottingOption.ADD_NEW_WORKBOOK
            or option is PlottingOption.ADD_NEW_WORKSHEET
            or (option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET and not keys)
        ):
            widget: RangedPlot = RangedPlot()
            countableDock = CountableDock("")
            countableDock.addWidget(widget)
            dock = currentSubwindow.widget().addDock(countableDock, "bottom")
        elif option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET:
            dock = currentSubwindow.widget().docks[keys[-1]]
        elif option is PlottingOption.ADD_IN_GIVEN_WORKSHEET:
            if dock is None:
                self.__logger.debug(f"Given dock {dock} is not valid.")
        else:
            raise NotImplementedError
        return dock

    def selectSubwindow(self, option):
        currentSubwindow = self.plotArea.mdiArea.currentSubWindow()
        if option is PlottingOption.ADD_NEW_WORKBOOK or (
            (
                option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET
                or option is PlottingOption.ADD_NEW_WORKSHEET
            )
            and currentSubwindow is None
            and not self.plotArea.mdiArea.subWindowList()
        ):
            self.plotArea.addWorkbook("Untitled")
            currentSubwindow = self.plotArea.mdiArea.subWindowList()[-1]
        elif (
            option == PlottingOption.ADD_NEW_WORKSHEET
            or option is PlottingOption.APPEND_IN_CURRENT_WORKSHEET
        ):
            # The first subwindow is not active, so find it manually.
            if currentSubwindow is None:
                currentSubwindow = self.plotArea.mdiArea.subWindowList()[-1]
        elif option is PlottingOption.ADD_IN_GIVEN_WORKSHEET:
            return None
        else:
            raise NotImplementedError
        return currentSubwindow

    def loadCsv(self, filename):
        dataFrame = pd.read_csv(filename)
        return dataFrame

    def loadHdf5(self, filename):
        f = h5py.File(filename, "r")
        # dlg = TimestampDialog(keys=getAllKeysHdf5(f))
        # dlg.optionsChosen.connect(self.onOpenFileOptionsChosen)
        # dlg.exec_()
        return f

    def onOpenFileOptionsChosen(self, options):
        self.options = options
        self.__logger.debug(options)

    def extractDataFromHdf5(self, datasetName, indices=None):
        data = np.array(self.file.get(datasetName))
        shape = data.shape
        self.__logger.debug(f"{datasetName} {shape} is going to be plotted.")
        listZeros = ["0" for _ in range(len(shape) - 1)]
        defaultText = "[" + ", ".join(listZeros) + ", :]"

        if len(shape) > 1:

            if indices is None:
                dialog = SizedInputDialog(self, QSize(400, 200))
                indices, okPressed = dialog.getText(
                    self,
                    f"Index selection",
                    f"The selected dataset has dimensions: {shape}. \n"
                    f"Enter below the indices to be plotted. \n\n"
                    f"Example: [1,:]",
                    text=defaultText,
                )

                if not okPressed:
                    return

            try:
                toBeEvaluated = "data" + indices
                dataToBePlotted = eval(toBeEvaluated)
            except SyntaxError:
                return

            fullDatasetName = datasetName + indices

        else:
            dataToBePlotted = data
            fullDatasetName = datasetName

        return dataToBePlotted, fullDatasetName

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

    @staticmethod
    def getWorkspaceDirectory() -> str:
        """
        Returns starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        return "workspace"

    @staticmethod
    def getWorkspaceFilter() -> str:
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "JSON (*.json);;All files (*)"

    def createActions(self) -> None:
        super().createActions()

        self.openWorkspaceAct = self.createAction(
            "&Open workspace",
            self.openWorkspace,
            "Open workspace",
            QKeySequence("Ctrl+Shift+o"),
        )

    def createFileMenu(self):
        super().createFileMenu()
        self.fileMenu.addAction(self.openWorkspaceAct)

    def createToolBars(self) -> None:
        super().createToolBars()
        self.fileToolBar.addAction(self.openWorkspaceAct)

    def openWorkspace(self, filename):
        self.plotArea.mdiArea.closeAllSubWindows()
        if filename in ["", None, False]:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open workspace from file",
                dir=PlotterWindow.getWorkspaceDirectory(),
                filter=PlotterWindow.getWorkspaceFilter(),
            )

        with open(filename) as file:
            rawData = file.read()
            try:
                data = json.loads(rawData, encoding="utf-8")
                self.workspaceName = filename
                for key in data:
                    worksheetArea = WorksheetArea()
                    worksheetArea.restoreCurves.connect(self.restoreCurve)
                    worksheetArea.restoreState(data[key])
                    self.plotArea.mdiArea.addSubWindow(worksheetArea)

            except json.JSONDecodeError:
                raise ValueError(
                    f"{os.path.basename(filename)} is not a valid JSON file"
                )
            except Exception as e:
                dumpException(e)

    def restoreCurve(self, worksheet: RangedPlot):
        for curveName in worksheet.curveNames:
            self.plotData(
                curveName,
                option=PlottingOption.ADD_IN_GIVEN_WORKSHEET,
                worksheet=worksheet,
            )

    def saveFile(self, fileName: str = ""):
        if not isinstance(fileName, str):
            fileName = ""
        self.__logger.debug("Saving graph")
        if not self.hasWorkspaceName:
            self.workspaceName, _ = QFileDialog.getSaveFileName(
                parent=self,
                caption="Save graph to file",
                dir=PlotterWindow.getWorkspaceDirectory() + fileName,
                filter=PlotterWindow.getWorkspaceFilter(),
            )

            if self.workspaceName is "":
                return

        state = {}
        workbook: QMdiSubWindow
        for workbook in self.plotArea.mdiArea.subWindowList():
            worksheetArea: WorksheetArea = workbook.widget()
            worksheetAreaState = worksheetArea.saveState()
            self.__logger.debug(worksheetAreaState)
            state[f"{workbook.windowTitle()}"] = worksheetAreaState

        self.__logger.debug(state)

        with open(self.workspaceName, "w") as file:
            file.write(json.dumps(state, indent=4, default=convert))
            self.__logger.info(f"Saving to {self.workspaceName} was successful.")

    def saveFileAs(self):
        workspaceName = self.workspaceName
        self.workspaceName = ""
        self.saveFile(workspaceName)

    def newFile(self):
        self.plotArea.addWorkbook()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = PlotterWindow()
    window.showMaximized()

    # FIXME: delete the following. Only for dev.
    # Open file
    # window.openWorkspace("workspace/example.json")
    # window.openFile("../../data/test.hdf5")
    window.openFile("../../data/mytestfile.hdf5")
    # window.plotData("sim_data/pos_k_i_dt", indices="[0,0,:]")
    # window.plotData("/cf1/pos")
    # window.openFile("../../data/h5ex_t_float.h5")

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
