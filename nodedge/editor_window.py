# -*- coding: utf-8 -*-
"""
Editor window module containing :class:`~nodedge.editor_window.EditorWindow` class.
"""
import json
import logging
import os
from typing import Callable, Dict, List, Optional, Union, cast

from PySide6.QtCore import QSettings, QSize, QStandardPaths, Qt, Signal
from PySide6.QtGui import (
    QAction,
    QClipboard,
    QCloseEvent,
    QGuiApplication,
    QIcon,
    QKeySequence,
)
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from nodedge.editor_widget import EditorWidget
from nodedge.scene_coder import SceneCoder
from nodedge.solver_dialog import SolverDialog

logger = logging.getLogger(__name__)


class EditorWindow(QMainWindow):
    """
    :class:`~nodedge.editor_window.EditorWindow` class

    The editor window is the base of the multi document interface (MDI)
    :class:`~nodedge.mdi_window.MdiWindow`.

    The application can be opened with the
    :class:`~nodedge.editor_window.EditorWindow` as main window, even if it is not
    the main use case.
    """

    EditorWidgetClass = EditorWidget

    recentFilesUpdated = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None):
        """
        :Instance Attributes:

        - **name_company** - name of the company, used for permanent profile settings
        - **name_product** - name of this App, used for permanent profile settings
        """

        super().__init__(parent)

        self.companyName = "Nodedge"
        self.productName = "Nodedge"

        self.instance: QGuiApplication = cast(
            QGuiApplication, QGuiApplication.instance()
        )

        # self.styler = ApplicationStyler()

        self.clipboard: QClipboard = self.instance.clipboard()

        # Pycharm does not recognise resolve connect method so the inspection is
        # noinspection PyUnresolvedReferences
        self.clipboard.dataChanged.connect(self.onClipboardChanged)  # type: ignore

        self.lastActiveEditorWidget: Optional[EditorWidget] = None
        self.debugMode: bool = False
        self.recentFiles: List[str] = []
        self.recentFilesActions: List[QAction] = []

        self.actionsDict: Dict[str, dict] = {}
        self.initUI()

    @property
    def currentEditorWidget(self) -> Optional[EditorWidget]:
        """
        :getter: Get current :class:`~nodedge.editor_widget.EditorWidget`

        .. note::

            The :class:`~nodedge.editor_window.EditorWindow` has only one
            :class:`~nodedge.editor_widget.EditorWidget`. This method is overridden
            by the :class:`~nodedge.mdi_window.MdiWindow` which may have several
            :class:`~nodedge.editor_widget.EditorWidget`.

        :rtype: Optional[:class:`~nodedge.editor_widget`]
        """
        centralWidget = self.centralWidget()
        if isinstance(centralWidget, EditorWidget):
            return centralWidget
        else:
            raise TypeError("Central widget is not an editor widget")

    # noinspection PyAttributeOutsideInit
    def initUI(self) -> None:
        """
        Set up this ``QMainWindow``.

        Create :class:`~nodedge.editor_widget.EditorWidget`, Actions and Menus
        """

        self.editorWidget = self.__class__.EditorWidgetClass()
        self.setCentralWidget(self.editorWidget)
        self.editorWidget.scene.addHasBeenModifiedListener(self.updateTitle)

        self.createActions()

        self.createMenus()

        # Initialize status bar
        self.createStatusBar()

        # Set window properties
        # Use sizeHint instead of forced size.
        # self.setGeometry(960, 30, 960, 960)
        self.updateTitle()
        self.show()

    # noinspection PyAttributeOutsideInit
    def createStatusBar(self) -> None:
        """
        Create Status bar and connect to
        :class:`~nodedge.graphics_view.GraphicsView`'s scenePosChanged event.
        """
        self.statusBar().showMessage("")
        self.statusMousePos = QLabel("")
        self.simulationProgressLabel = QLabel("")
        self.simulationProgressBar = QProgressBar()
        self.simulationProgressBar.setFixedWidth(400)
        self.simulationProgressBar.setRange(0, 100)
        self.statusBar().addPermanentWidget(self.simulationProgressLabel)
        self.statusBar().addPermanentWidget(self.simulationProgressBar)
        self.statusBar().addWidget(self.statusMousePos)

        if self.currentEditorWidget is None:
            return

        self.currentEditorWidget.graphicsView.scenePosChanged.connect(
            self.OnScenePosChanged
        )

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createActions(self) -> None:
        """
        Create basic `File` and `Edit` actions.
        """

        self.newAct = self.createAction(
            "&New",
            self.newFile,
            "Create new Nodedge model",
            QKeySequence("Ctrl+N"),
            category="File",
        )

        self.openAct = self.createAction(
            "&Open",
            self.openFile,
            "Open file",
            QKeySequence("Ctrl+O"),
            category="File",
        )

        self.saveAct = self.createAction(
            "&Save",
            self.saveFile,
            "Save file",
            QKeySequence("Ctrl+S"),
            category="File",
        )

        self.saveAsAct = self.createAction(
            "Save &As",
            self.saveFileAs,
            "Save file as...",
            QKeySequence("Ctrl+Shift+S"),
            category="File",
        )

        self.undoAct = self.createAction(
            "&Undo",
            self.undo,
            "Undo last operation",
            QKeySequence("Ctrl+Z"),
            category="Edit",
        )

        self.redoAct = self.createAction(
            "&Redo",
            self.redo,
            "Redo last operation",
            QKeySequence("Ctrl+Shift+Z"),
            category="Edit",
        )

        self.cutAct = self.createAction(
            "C&ut",
            self.cut,
            "Cut selected items",
            QKeySequence("Ctrl+X"),
            category="Edit",
        )

        self.copyAct = self.createAction(
            "&Copy",
            self.copy,
            "Copy selected items",
            QKeySequence("Ctrl+C"),
            category="Edit",
        )

        self.pasteAct = self.createAction(
            "&Paste",
            self.paste,
            "Paste selected items",
            QKeySequence.Paste,
            category="Edit",
        )

        self.deleteAct = self.createAction(
            "&Delete",
            self.delete,
            "Delete selected items",
            QKeySequence("Del"),
            category="Edit",
        )

        self.fitToViewAct = self.createAction(
            "Fit to view",
            self.onFitToView,
            "Fit content to view",
            QKeySequence(Qt.Key_Space),
            category="View",
        )

        self.generateCodeAct = self.createAction(
            "Generate code",
            self.onGenerateCode,
            "Generate python code",
            QKeySequence("Ctrl+G"),
            category="Coder",
        )

        self.configureSolverAct = self.createAction(
            "Configure solver",
            self.configureSolver,
            "Configure solver",
            QKeySequence("Ctrl+K"),
            category="Simulation",
        )

        self.showCodeAct = self.createAction(
            "Show code",
            self.onShowCode,
            "Show python code",
            QKeySequence("Ctrl+Shift+C"),
            category="Coder",
        )
        self.showCodeAct.setEnabled(False)

        self.showGraphAct = self.createAction(
            "Show graph",
            self.onShowGraph,
            "Show graph",
            QKeySequence("Ctrl+Shift+G"),
            category="Dats",
        )
        self.showGraphAct.setEnabled(False)

        self.evalAct = self.createAction(
            "Evaluate all nodes",
            self.evaluateAllNodes,
            "",
            QKeySequence("Ctrl+Space"),
            category="Coder",
        )

        self.startSimulationAct = self.createAction(
            "Start simulation",
            self.onStartSimulation,
            "Start the simulation of the current model",
            QKeySequence("Ctrl+Shift+S"),
            category="Simulation",
        )
        self.startSimulationAct.setIcon(QIcon("resources/lucide/play.svg"))

        self.stopSimulationAct = self.createAction(
            "Stop simulation",
            self.onStopSim,
            "Stop the running simulation",
            category="Simulation",
        )
        self.stopSimulationAct.setIcon(QIcon("resources/lucide/square.svg"))

        self.pauseSimulationAct = self.createAction(
            "Pause simulation",
            self.onPauseSim,
            "Pause the running simulation",
            category="Simulation",
        )
        self.pauseSimulationAct.setIcon(QIcon("resources/lucide/pause.svg"))

        self.takeScreenshotAct = self.createAction(
            "Take screenshot",
            self.takeScreenshot,
            "Take a screenshot of the current view",
            QKeySequence("Ctrl+Shift+Space"),
            category="File",
        )

        self.helpAct = self.createAction(
            "&Help",
            self.onHelp,
            "Help",
            QKeySequence("F1"),
            category="Help",
        )

        self.realTimeEvalAct = self.createAction(
            "Real-time evaluation",
            self.onRealTimeEval,
            "Evaluate model in real time",
            QKeySequence("Ctrl+Shift+A"),
            category="Simulator",
        )
        self.realTimeEvalAct.setCheckable(True)
        self.realTimeEvalAct.setIcon(QIcon("resources/lucide/alarm-check.svg"))

    def onRealTimeEval(self, checked: bool) -> None:
        """
        Enable/disable real-time evaluation.
        """
        if self.currentEditorWidget is None:
            return
        if hasattr(self.currentEditorWidget, "scene") is False:
            return
        self.currentEditorWidget.scene.realTimeEval = checked
        if checked:
            self.currentEditorWidget.evalNodes()

    def onHelp(self):
        pass

    def onStopSim(self) -> None:
        if self.currentEditorWidget is None:
            return
        self.currentEditorWidget.scene.simulator.stop()
        self.simulationProgressLabel.setText("")
        self.simulationProgressBar.setValue(0)

    def onPauseSim(self) -> None:
        if self.currentEditorWidget is None:
            return
        self.currentEditorWidget.scene.simulator.pause()

    def takeScreenshot(self, filename=None):
        """
        Take screenshot
        """
        logger.debug("Take screenshot")
        if filename is None:
            filename, _ = QFileDialog.getSaveFileName(
                parent=self,
                caption="Save graph to file",
                dir=EditorWindow.getFileDialogDirectory(),
                filter="PNG (*.png);; JPG (*.jpg);; JPEG (*.jpeg)",
            )

        if not filename:
            return

        self.currentEditorWidget.scene.graphicsView.grab().save(filename)

    def onStartSimulation(self):
        self.currentEditorWidget.scene.simulator.run()
        self.currentEditorWidget.scene.simulator.progressed.connect(
            self.updateProgressLabel
        )

    def updateProgressLabel(self, progress):
        totalSteps = self.currentEditorWidget.scene.simulator.totalSteps
        finalTime = self.currentEditorWidget.scene.simulator.config.finalTime
        currentTime = self.currentEditorWidget.scene.simulator.currentTimeStep
        currentStep = self.currentEditorWidget.scene.simulator.currentStep
        stepsPerSecond = self.currentEditorWidget.scene.simulator.stepsPerSecond
        percentPerSecond = stepsPerSecond / totalSteps * 100
        percentProgress = currentStep / totalSteps * 100
        self.simulationProgressBar.setValue(int(percentProgress))
        self.simulationProgressLabel.setText(
            f"Progress: {currentTime:.1E} s/{finalTime:.1E} s [{percentProgress:.0f}%] [{percentPerSecond:.0E} %/s]"
        )
        self.simulationProgressLabel.setToolTip(
            f"{currentStep:.0E}/{totalSteps:.0E} [{percentProgress:.0E}]% [{stepsPerSecond:.0E} steps/s]"
        )

    def onShowGraph(self):
        QMessageBox.information(self, "Graph", "Show graph")

    def onShowCode(self):
        """
        Show the generated code.
        """

        dialog = QDialog(self)
        dialog.setMinimumWidth(600)
        dialog.setWindowTitle("Code")
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(QLabel(f"{self.currentEditorWidget.shortName} code:"))
        codeEdit = QTextEdit()
        codeEdit.setReadOnly(True)
        codeEdit.setPlainText(self.currentEditorWidget.scene.coder.generatedCode)
        dialog.layout().addWidget(codeEdit)

        dialog.showMaximized()

    def evaluateAllNodes(self):
        for n in self.editorWidget.scene.nodes:
            n.eval()

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createMenus(self) -> None:
        """
        Create Menus for `File` and `Edit`.
        """
        self.createFileMenu()
        self.createEditMenu()
        self.createViewMenu()
        self.createCoderMenu()
        self.createSimulationMenu()

    def createSimulationMenu(self) -> None:
        """
        Create the simulation menu.
        """
        self.simMenu: QMenu = self.menuBar().addMenu("&Simulation")
        self.simMenu.addAction(self.configureSolverAct)
        self.simMenu.addSeparator()
        self.simMenu.addAction(self.showGraphAct)
        self.simMenu.addSeparator()
        self.simMenu.addAction(self.startSimulationAct)
        self.simMenu.addAction(self.pauseSimulationAct)
        self.simMenu.addAction(self.stopSimulationAct)
        self.simMenu.addSeparator()
        self.simMenu.addAction(self.evalAct)

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createCoderMenu(self):
        self.coderMenu: QMenu = self.menuBar().addMenu("&Coder")
        self.coderMenu.addAction(self.generateCodeAct)
        self.coderMenu.addAction(self.showCodeAct)

    def configureSolver(self):
        if self.currentEditorWidget is None:
            QMessageBox.warning(self, "No model", "No model is open.")
            return
        simulatorConfig = self.currentEditorWidget.scene.simulator.config
        self.solverDialog = SolverDialog(simulatorConfig)
        self.solverDialog.solverConfigChanged.connect(
            self.currentEditorWidget.scene.simulator.updateConfig
        )
        self.solverDialog.show()

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createFileMenu(self):
        """
        Create `File` Menu.
        """
        self.fileMenu: QMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openAct)
        self.recentFilesMenu = self.fileMenu.addMenu("Open recent")
        self.updateRecentFilesMenu()
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.takeScreenshotAct)

    def updateRecentFilesMenu(self):
        self.recentFilesMenu.clear()
        for action in self.recentFilesActions:
            action.deleteLater()
        self.recentFilesActions = []
        logger.debug("Creating new recent files actions")

        for index, filePath in enumerate(self.recentFiles):
            if index >= 8:
                break
            logger.debug(f"Creating action for {filePath}")

            shortpath = filePath.replace("\\", "/")
            shortpath = shortpath.split("/")[-1]
            action = self.createAction(
                shortpath,
                lambda: self.openFile(filePath),
                f"Open {filePath}",
                QKeySequence(f"Ctrl+Shift+{index+1}"),
            )
            self.recentFilesMenu.addAction(action)
            self.recentFilesActions.append(action)

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createEditMenu(self):
        """
        Create `Edit` Menu.
        """
        self.editMenu: QMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.deleteAct)

    # noinspection PyAttributeOutsideInit
    def createViewMenu(self) -> None:
        """
        Create view menu.
        """
        self.viewMenu: QMenu = self.menuBar().addMenu("&View")
        self.viewMenu.addAction(self.fitToViewAct)

    def sizeHint(self) -> QSize:
        """
        Qt size hint handle.
        TODO: Investigate if we really need to overwrite this method.

        :return: ``None``
        """
        return QSize(800, 600)

    def updateTitle(self) -> None:
        """
        Update window title according to the name of the file currently opened.
        """
        if self.currentEditorWidget:
            title = "Create Nodedge"
            if self.currentEditorWidget.hasName:
                title += f" with {self.currentEditorWidget.userFriendlyFilename}"

            else:
                title += "!"

                if self.currentEditorWidget.isModified:
                    title += "*"
            self.setWindowTitle(title)

            self.currentEditorWidget.updateTitle()
            self.showCodeAct.setEnabled(False)

    def onClipboardChanged(self) -> None:
        """
        Slot called when the clipboard has changed.

        :return: ``None``
        """
        logger.debug(f"Clipboard changed: '{self.clipboard.text()}'")

    def OnScenePosChanged(self, x: float, y: float):
        """
        Handle event when cursor position changed on the :class:`~nodedge.scene.Scene`.
        :param x: new cursor x position
        :type x: float
        :param y: new cursor y position
        :type y: float
        """
        self.statusMousePos.setText(f"Scene pos: {x:.2f}, {y:.2f}")

    def newFile(self):
        """
        Open a clean new file in the window's editor.

        Confirmation is asked to the user if there are unsaved changes.
        """
        if self.maybeSave():
            logger.info("Creating new model")
            self.currentEditorWidget.newFile()
        self.updateTitle()

    def openFile(self, filename):
        """
        Open a file in the window's editor from its filename.

        Confirmation is asked to the user if there are unsaved changes.

        :param filename: absolute path and filename of the file to open.
        :type filename: ``str``
        """
        logger.debug("Opening graph")
        if self.maybeSave():
            if filename is None:
                filename, ok = QFileDialog.getOpenFileName(
                    parent=self,
                    caption="Open graph from file",
                    dir=EditorWindow.getFileDialogDirectory(),
                    filter=EditorWindow.getFileDialogFilter(),
                )

            if filename == "":
                self.newFile()
            if os.path.isfile(filename):
                self.currentEditorWidget.loadFile(filename)
                self.statusBar().showMessage(
                    f"Successfully opened {os.path.basename(filename)}", 5000
                )

                self.updateTitle()

        self.fitToViewAct.trigger()

    def saveFile(self):
        """
        Save serialized JSON version of the currently opened file, in a JSON file
        based on the editor's filename.
        """
        logger.warning("Saving graph")
        if not self.currentEditorWidget.hasName:
            self.saveFileAs()

        else:
            self.currentEditorWidget.saveFile(self.currentEditorWidget.filename)

        if self.currentEditorWidget.hasName:
            self.saveSnapshot()
            self.addToRecentFiles(self.currentEditorWidget.filename)

            self.statusBar().showMessage(
                f"Successfully saved to {self.currentEditorWidget.shortName}", 5000
            )
        else:
            self.statusBar().showMessage(f"Save aborted", 5000)
        self.updateTitle()
        self.currentEditorWidget.updateTitle()

    def saveSnapshot(self):
        data_path = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
        filename = self.currentEditorWidget.filename
        filename = filename.replace("\\", "_")
        filename = filename.replace("/", "_")
        filename = filename.replace(":", "_")
        filename = filename.replace(".json", "")

        filePath = os.path.join(data_path, filename + ".png")

        if not os.path.exists(data_path):
            os.makedirs(data_path)

        # self.onFitInView()
        self.currentEditorWidget.graphicsView.graphicsScene.fitToView()
        self.takeScreenshot(filePath)

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

    def saveFileAs(self):
        """
        Save serialized JSON version of the currently opened file, allowing the user
        to choose the filename via a ``QFileDialog``.
        """
        logger.debug("Saving graph as...")
        filename, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save graph to file",
            dir=EditorWindow.getFileDialogDirectory(),
            filter=EditorWindow.getFileDialogFilter(),
        )

        if filename in [None, "", ""]:
            return

        self.beforeSaveFileAs(self.currentEditorWidget, filename)
        self.currentEditorWidget.saveFile(filename)
        self.statusBar().showMessage(
            f"Successfully saved to {self.currentEditorWidget.shortName}", 5000
        )
        self.updateTitle()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Close the window.

        Confirmation is asked to the user if there are unsaved changes.
        """
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def quit(self) -> None:
        """
        Callback when the user decides to close the application.

        :return: ``None``
        """
        self.close()

    def undo(self) -> None:
        """
        Undo last operation.
        """
        logger.debug("Undoing last action")
        if self.currentEditorWidget:
            self.currentEditorWidget.scene.history.undo()

    def redo(self) -> None:
        """
        Redo previously cancelled operation.
        """
        logger.debug("Redoing last action")
        if self.currentEditorWidget:
            self.currentEditorWidget.scene.history.redo()

    def delete(self) -> None:
        """
        Delete selected items.
        """
        logger.debug("Deleting selected items")
        if self.currentEditorWidget:
            self.currentEditorWidget.graphicsView.deleteSelected()

    def cut(self) -> None:
        """
        Cut to clipboard selected items.
        """
        logger.debug("Cutting selected items")
        if self.currentEditorWidget:
            data = self.currentEditorWidget.scene.clipboard.serializeSelected(
                delete=True
            )
            strData = json.dumps(data, indent=4)
            self.clipboard.setText(strData)

    def copy(self) -> None:
        """
        Copy to clipboard selected items.
        """
        logger.debug("Copying selected items")
        if self.currentEditorWidget:
            data = self.currentEditorWidget.scene.clipboard.serializeSelected()
            strData = json.dumps(data, indent=4)
            logger.debug(strData)
            self.clipboard.setText(strData)

    def paste(self):
        """
        Paste from clipboard, creating items after deserialization.
        """
        logger.debug("Pasting saved items in clipboard")
        if self.currentEditorWidget:
            rawData = self.clipboard.text()
            try:
                data = json.loads(rawData)
            except ValueError as e:
                logger.debug(f"Pasting of not valid json data: {e}")
                return

            # Check if json data are correct
            if "nodes" not in data:
                logger.debug("JSON does not contain any blocks!")

            self.currentEditorWidget.scene.clipboard.deserialize(data)

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

    @staticmethod
    def getFileDialogFilter() -> str:
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "Graph (*.json);;All files (*)"

    def maybeSave(self):
        """
        If current :class:`~nodedge.scene.Scene` is modified, ask a dialog to save
        the changes.

        :return: ``True`` if the action calling this method is allowed to continue.
                 ``False`` if we should cancel operation.
        :rtype: ``bool``
        """

        if self.currentEditorWidget is None or not self.currentEditorWidget.isModified:
            return True

        res = QMessageBox.warning(
            self,
            "Nodedge is about to close",
            "There are unsaved modifications. \n" "Do you want to save your changes?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

        if res == QMessageBox.StandardButton.Save:
            return self.saveFile()
        elif res == QMessageBox.StandardButton.Cancel:
            return False
        elif res == QMessageBox.StandardButton.Discard:
            self.currentEditorWidget.scene.isModified = False
            return True

        return True

    def readSettings(self):
        """
        Read the permanent profile settings for this application.
        """
        settings = QSettings(self.companyName, self.productName)
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("windowState"))
        debugMode = settings.value("debug", False)
        if debugMode == "false":
            self.debugMode = False
        elif debugMode == "true":
            self.debugMode = True
        else:
            self.debugMode = debugMode
        self.recentFiles = list(settings.value("recent_files", []))
        self.updateRecentFilesMenu()

    def writeSettings(self):
        """
        Write the permanent profile settings for this application.
        """
        settings = QSettings(self.companyName, self.productName)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("debug", self.debugMode)

        self.writeRecentFilesSettings()

    def writeRecentFilesSettings(self):
        """
        Write the recent files settings for this application.
        """
        settings = QSettings(self.companyName, self.productName)
        settings.setValue("recent_files", self.recentFiles)

    def beforeSaveFileAs(
        self, currentEditorWidget: EditorWidget, filename: str
    ) -> None:
        """
        Event triggered after choosing filename and before actual fileSave(). Current
        :class:`~nodedge.editor_widget.EditorWidget` is passed because focus is lost
        after asking with ``QFileDialog`` and therefore `getCurrentNodeEditorWidget`
        will return ``None``.

        :param currentEditorWidget: :class:`~nodedge.editor_widget.EditorWidget`
            currently focused
        :type currentEditorWidget: :class:`~nodedge.editor_widget.EditorWidget`
        :param filename: name of the file to be saved
        :type filename: ``str``
        """
        pass

    def onFitToView(self):
        if self.currentEditorWidget is not None:
            self.currentEditorWidget.graphicsView.graphicsScene.fitToView()

    def onGenerateCode(self):
        if self.currentEditorWidget is not None:
            coder: SceneCoder = self.currentEditorWidget.scene.coder
            if coder is not None:
                self.currentEditorWidget.scene.coder.generateCodeAndSave()
                successStr = f"File saved to {coder.filename}"
                logger.debug(successStr)
                self.statusBar().showMessage(successStr, 5000)
                self.showCodeAct.setEnabled(True)

    def createAction(
        self,
        name: str,
        callback: Callable,
        statusTip: Optional[str] = None,
        shortcut: Union[None, str, QKeySequence, QKeySequence.StandardKey] = None,
        checkable: bool = False,
        category: str = "",
    ) -> QAction:
        """
        Create an action for this window and add it to actions list.

        :param name: action's name
        :type name: ``str``
        :param callback: function to be called when the action is triggered
        :type callback: ``Callable``
        :param statusTip: Description of the action displayed
            at the bottom left of the :class:`~nodedge.editor_window.EditorWindow`.
        :type statusTip: Optional[``str``]
        :param shortcut: Keyboard shortcut to trigger the action.
        :type shortcut: ``Optional[str]``
        :param checkable: if checkable, a mark will appear near the action in the menu when active.
        :type checkable: ``bool``
        :return:
        """
        act = QAction(parent=self, text=name, checkable=checkable)  # type: ignore
        act.triggered.connect(callback)

        if statusTip is not None:
            act.setStatusTip(statusTip)
            act.setToolTip(statusTip)

        if shortcut is not None:
            act.setShortcut(QKeySequence(shortcut))

        self.addAction(act)

        name = name.replace("&", "")

        if isinstance(shortcut, QKeySequence):
            shortcut = str(shortcut.toString(QKeySequence.NativeText))
        elif isinstance(shortcut, QKeySequence.StandardKey):
            shortcut = QKeySequence.keyBindings(shortcut)[0]
            shortcut = shortcut.toString()

        self.actionsDict.update(
            {
                name: {
                    "category": category,
                    "statusTip": statusTip,
                    "shortcut": shortcut,
                    "action": act,
                }
            }
        )

        return act  # type: ignore
