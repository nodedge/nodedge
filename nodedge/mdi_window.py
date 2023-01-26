# -*- coding: utf-8 -*-
"""Multi Document Interface window module containing
:class:`~nodedge.mdi_window.MdiWindow` class. """
import logging
import os
from typing import Any, Callable, List, Optional, cast

from PySide6.QtCore import QPointF, QSignalMapper, QSize, Qt, QTimer, Slot
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QKeySequence, QMouseEvent
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMdiSubWindow,
    QMenu,
    QMessageBox,
    QToolBar,
    QWidget,
)

from nodedge.action_palette import ActionPalette
from nodedge.console_widget import ConsoleWidget
from nodedge.editor_widget import EditorWidget
from nodedge.editor_window import EditorWindow
from nodedge.history_list_widget import HistoryListWidget
from nodedge.home_menu import HomeMenu, MenuBar
from nodedge.mdi_area import MdiArea
from nodedge.mdi_widget import MdiWidget
from nodedge.node_tree_widget import NodeTreeWidget
from nodedge.scene_item_detail_widget import SceneItemDetailWidget
from nodedge.scene_items_table_widget import SceneItemsTableWidget
from nodedge.scene_items_tree_widget import SceneItemsTreeWidget

logger = logging.getLogger(__name__)


class MdiWindow(EditorWindow):
    """
    :class:`~nodedge.mdi_window.MdiWindow` class.

    The mdi window is the main window of Nodedge.
    """

    def __init__(self) -> None:
        self.currentEditorWidgetChangedListeners: List[Callable] = []
        super(MdiWindow, self).__init__()

    @property
    def currentEditorWidget(self) -> Optional[EditorWidget]:
        """
        Property representing the :class:`~nodedge.editor_widget.EditorWidget` of the
        active sub-window.

        .. note::

            This property cannot be set.

        :type: :class:`~nodedge.editor_widget.EditorWidget`
        """
        if not self.mdiArea.subWindowList():
            self.lastActiveEditorWidget = None
        activeSubWindow = self.mdiArea.activeSubWindow()
        if (
            activeSubWindow is not None
            and activeSubWindow.widget() is not None
            and isinstance(activeSubWindow.widget(), EditorWidget)
        ):
            self.lastActiveEditorWidget = cast(EditorWidget, activeSubWindow.widget())
        return self.lastActiveEditorWidget

    # noinspection PyAttributeOutsideInit
    def initUI(self) -> None:
        """
        Set up this ``QMainWindow``.

        Create the mdi area, actions and menus
        """
        self.companyName = "Nodedge"
        self.productName = "Nodedge"
        self.icon = QIcon(
            os.path.join(os.path.dirname(__file__), "../resources/nodedge_logo.png")
        )
        self.setWindowIcon(self.icon)
        self.setMinimumSize(QSize(880, 600))

        # self.styleSheetFilename = os.path.join(
        #     os.path.dirname(__file__), "../resources/qss/nodedge_style.qss"
        # )
        # loadStyleSheets(
        #     # os.path.join(os.path.dirname(__file__), "qss/calculator-dark.qss"),
        #     self.styleSheetFilename
        # )

        self.setMouseTracking(True)

        self.mdiArea = MdiArea()
        self.setCentralWidget(self.mdiArea)

        self.addCurrentEditorWidgetChangedListener(self.updateMenus)

        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)  # type: ignore

        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mappedObject.connect(self.setActiveSubWindow)  # type: ignore

        self.createSceneItemDetailDock()
        self.createNodesDock()
        self.createHistoryDock()
        # self.createSceneItemsDock()
        self.createSceneItemsTreeDock()
        self.createPythonConsole()

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.readSettings()
        self.updateMenus()

        self.setWindowTitle(self.productName)

    def createStatusBar(self) -> None:
        """
        Create the status bar describing Nodedge status and the mouse position.
        """
        super().createStatusBar()
        self.statusBar().showMessage("Ready")

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createActions(self) -> None:
        """
        Create `File`, `Edit` and `About` actions.
        """
        super().createActions()

        self.closeAct = self.createAction(
            "Cl&ose",
            self.mdiArea.closeActiveSubWindow,
            "Close the active window",
            category="File",
        )

        self.closeAllAct = self.createAction(
            "Close &All",
            self.mdiArea.closeAllSubWindows,
            "Close all the windows",
            category="File",
        )

        self.tileAct = self.createAction(
            "&Tile", self.mdiArea.tileSubWindows, "Tile the windows", category="View"
        )

        self.cascadeAct = self.createAction(
            "&Cascade",
            self.mdiArea.cascadeSubWindows,
            "Cascade the windows",
            category="View",
        )

        self.hideToolbarAct = self.createAction(
            "Hide toolbars",
            self.hideToolBars,
            "Hide toolbars",
            QKeySequence("Ctrl+T"),
            category="View",
        )

        self.nextAct = self.createAction(
            "Ne&xt",
            self.mdiArea.activateNextSubWindow,
            "Move the focus to the next window",
            QKeySequence.NextChild,
            category="View",
        )

        # noinspection SpellCheckingInspection
        self.previousAct = self.createAction(
            "Pre&vious",
            self.mdiArea.activatePreviousSubWindow,
            "Move the focus to the previous window",
            QKeySequence.PreviousChild,
            category="View",
        )

        # TODO: Implement zoomInAct
        # self.zoomInAct = self.createAction()

        self.nodeToolbarAct = self.createAction(
            "&Node libraries",
            self.onNodesToolbarTriggered,
            "Enable/Disable the node libraries",
            QKeySequence("ctrl+alt+n"),
            category="Help",
        )

        self.nodeToolbarAct.setCheckable(True)
        self.nodeToolbarAct.setChecked(True)  # self.nodesDock.isVisible()

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = self.createAction(
            "&About",
            self.about,
            "Show information about Nodedge",
            QKeySequence("Ctrl+H"),
            category="Help",
        )

        self.debugAct = self.createAction(
            "&Debug",
            self.onDebugSwitched,
            "Enable/Disable the debug mode",
            QKeySequence("ctrl+shift+d"),
            checkable=True,
            category="Help",
        )

        self.showDialogActionsAct = self.createAction(
            "Show dialog actions",
            self.onShowDialogActions,
            "Show available actions",
            QKeySequence("ctrl+shift+a"),
            category="Help",
        )

        self.addCommentElementAct = self.createAction(
            "Add comment",
            self.addCommentElement,
            "Add comment element in current model",
            QKeySequence("Ctrl+Alt+C"),
            category="Edit",
        )

    def evaluateAllNodes(self):
        if self.currentEditorWidget is None:
            return
        for n in self.currentEditorWidget.scene.nodes:
            n.isDirty = True
        for n in self.currentEditorWidget.scene.nodes:
            n.eval()

    # noinspection PyAttributeOutsideInit
    def createToolBars(self) -> None:
        """
        Create the `File` and `Edit` toolbar containing few of their menu actions.
        """
        self.toolBars = []
        self.fileToolBar: QToolBar = self.addToolBar("File")
        self.fileToolBar.setMovable(False)
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.addSeparator()
        self.toolBars.append(self.fileToolBar)

        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.setMovable(False)
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)
        self.editToolBar.addAction(self.addCommentElementAct)
        self.editToolBar.addSeparator()
        self.toolBars.append(self.editToolBar)
        #
        # self.coderToolBar = self.addToolBar("Coder")
        # self.coderToolBar.setMovable(False)
        # self.coderToolBar.addAction(self.generateCodeAct)
        # self.toolBars.append(self.coderToolBar)

        self.simuToolbar = QToolBar("Simulation")
        self.addToolBar(self.simuToolbar)
        self.simuToolbar.setMovable(False)
        self.simuToolbar.addAction(self.realTimeEvalAct)
        self.simuToolbar.addSeparator()
        self.simuToolbar.addAction(self.startSimulationAct)
        self.simuToolbar.addAction(self.pauseSimulationAct)
        self.simuToolbar.addAction(self.stopSimulationAct)
        self.simuToolbar.addAction(self.configureSolverAct)

    def hideToolBars(self):
        if self.toolBars[0].isVisible():
            for toolBar in self.toolBars:
                toolBar.hide()
        else:
            for toolBar in self.toolBars:
                toolBar.show()

    def createMenus(self) -> None:
        """
        Create `Window` and `Help` menus.

        `Window` menu allows to navigate between the sub-windows.
        `Help` menu allows to display know more about Nodedge.
        """
        self.menubar = MenuBar(self)
        self.setMenuBar(self.menubar)
        self.homeMenu = self.menubar.homeMenu
        self.homeMenu.aboutToShow.connect(self.closeHomeMenu)

        # self.createHomeMenu()

        super().createMenus()
        self.createWindowMenu()
        self.createHelpMenu()

        # noinspection PyUnresolvedReferences
        self.editMenu.aboutToShow.connect(self.updateEditMenu)  # type: ignore

    # noinspection PyAttributeOutsideInit
    def createHomeMenu(self):
        # QIcon("../resources/white_icons/home_page.png")
        self.homeMenu = HomeMenu(self)
        self.menuBar().addMenu(self.homeMenu)

        # self.homeMenu.aboutToShow.connect(self.closeHomeMenu)

    def closeHomeMenu(self):
        timer = QTimer(self)
        timer.singleShot(1, self.homeMenu.hide)

    # noinspection PyAttributeOutsideInit
    def createHelpMenu(self) -> None:
        """
        Create help menu, containing about action.
        """
        self.helpMenu: QMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.debugAct)
        self.helpMenu.addAction(self.showDialogActionsAct)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.helpAct)

    # noinspection PyAttributeOutsideInit
    def createWindowMenu(self) -> None:
        """
        Create window menu, containing window navigation actions.
        """
        self.windowMenu = self.menuBar().addMenu("&Window")
        # noinspection PyUnresolvedReferences
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)  # type: ignore

    def updateMenus(self) -> None:
        """
        Update menus accordingly to the presence or not of sub-window in the editor,
        enabling and disabling file manipulation actions, for example.
        """

        self.updateFileMenu()
        self.updateEditMenu()
        self.updateWindowMenu()

    def updateFileMenu(self) -> None:
        """
        Update file menu.
        """
        active = self.currentEditorWidget
        hasMdiChild = active is not None
        self.saveAct.setEnabled(hasMdiChild)
        self.saveAsAct.setEnabled(hasMdiChild)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)

    def updateWindowMenu(self) -> None:
        """
        Update window menu.
        """
        active = self.currentEditorWidget
        hasMdiChild = active is not None
        self.windowMenu.clear()
        self.windowMenu.addAction(self.nodeToolbarAct)

        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)

        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)

        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            widget: QWidget = window.widget()
            if not isinstance(widget, EditorWidget):
                logger.warning(
                    "The widget of the sub window should be an 'editor widget'"
                )
            editorWidget: EditorWidget = cast(EditorWidget, widget)

            text = f"{i + 1} {editorWidget.userFriendlyFilename}"
            if i < 9:
                text = "&" + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(editorWidget is self.currentEditorWidget)
            # noinspection PyUnresolvedReferences
            action.triggered.connect(self.windowMapper.map)  # type: ignore
            self.windowMapper.setMapping(action, window)

    def updateEditMenu(self) -> None:
        """
        Update edit menu.
        """
        # logger.debug("Update edit menu")

        active = self.currentEditorWidget
        if active is None:
            return
        hasMdiChild = active is not None

        self.pasteAct.setEnabled(hasMdiChild)

        hasSelection = hasMdiChild and active.hasSelectedItems
        self.cutAct.setEnabled(hasSelection)
        self.copyAct.setEnabled(hasMdiChild and active.hasSelectedItems)

        self.undoAct.setEnabled(hasMdiChild and active.canUndo)
        self.redoAct.setEnabled(hasMdiChild and active.canRedo)

    def _createMdiSubWindow(
        self, childWidget: Optional[MdiWidget] = None
    ) -> QMdiSubWindow:
        """
        Create a new sub window containing a
        :class:`~nodedge.editor_widget.EditorWidget`
        """
        editor: MdiWidget = childWidget if childWidget is not None else MdiWidget()
        editor.scene.coder.notConnectedSocket.connect(
            self.onSceneCoderOutputSocketDisconnect
        )
        subWindow = self.mdiArea.addSubWindow(editor)
        self.mdiArea.setActiveSubWindow(subWindow)

        icon = QIcon(".")
        subWindow.setWindowIcon(icon)
        editor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        editor.scene.history.addHistoryModifiedListener(self.historyListWidget.update)
        # editor.scene.history.addHistoryModifiedListener(
        #     self.sceneItemsTableWidget.update
        # )
        editor.scene.addItemsDeselectedListener(self.sceneItemDetailsWidget.update)
        editor.scene.addItemSelectedListener(self.sceneItemDetailsWidget.update)
        editor.addCloseEventListener(self.onSubWindowClosed)

        return subWindow

    def onSubWindowClosed(self, widget: EditorWidget, event: QCloseEvent) -> None:
        """
        Slot called when sub window is being closed.

        :param widget:
        :type widget: ``EditorWidget``
        :param event:
        :type event: ``QCloseEvent.py``
        """
        subWindowToBeDeleted = self.findMdiSubWindow(widget.filename)
        if subWindowToBeDeleted is None:
            return

        self.mdiArea.setActiveSubWindow(subWindowToBeDeleted)
        # self.sceneItemsTableWidget.scene = None
        self.sceneItemsTreeWidget.scene = None
        # self.sceneItemsTableWidget.clearContents()

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def findMdiSubWindow(self, filename: str) -> Optional[QMdiSubWindow]:
        """
        Find the sub window containing the file which name has been given as parameter.

        :param filename: the filename to be looked for
        :return: The sub window containing the appropriate file
        :rtype: ``QMdiSubWindow``
        """
        for window in self.mdiArea.subWindowList():
            editorWidget: EditorWidget = cast(EditorWidget, window.widget())
            if editorWidget.filename == filename:
                return window
        return None

    def setActiveSubWindow(self, window: QMdiSubWindow) -> None:
        """
        Setter for active sub window.

        :param window:
        :type window: ``QMdiSubWindow``
        :return:
        """

        if window:
            self.mdiArea.setActiveSubWindow(window)

    # noinspection PyAttributeOutsideInit
    def createSceneItemDetailDock(self) -> None:
        """
        Create Item detail dock.
        """
        self.sceneItemDetailsWidget = SceneItemDetailWidget(self)

        self.sceneItemDetailsDock = QDockWidget("Node details")
        self.sceneItemDetailsDock.setWidget(self.sceneItemDetailsWidget)
        self.sceneItemDetailsDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.sceneItemDetailsDock)

    # noinspection PyAttributeOutsideInit
    def createNodesDock(self) -> None:
        """
        Create Nodes dock.
        """
        self.nodesTreeWidget = NodeTreeWidget()
        self.nodesTreeWidget.itemsPressed.connect(self.showItemsInStatusBar)

        self.nodesDock = QDockWidget("Node libraries")
        self.nodesDock.setWidget(self.nodesTreeWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)

    # noinspection PyAttributeOutsideInit
    def createHistoryDock(self) -> None:
        """
        Create history dock.
        """
        self.historyListWidget = HistoryListWidget(self)
        self.historyListWidget.itemsPressed.connect(self.showItemsInStatusBar)
        self.addCurrentEditorWidgetChangedListener(self.historyListWidget.update)

        self.historyDock = QDockWidget("History")
        self.historyDock.setWidget(self.historyListWidget)
        self.historyDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.historyDock)

    # noinspection PyAttributeOutsideInit
    def createSceneItemsDock(self) -> None:
        """
        Create scene items dock.
        """
        self.sceneItemsTableWidget = SceneItemsTableWidget(self)
        # self.sceneItemsTableWidget.itemsPressed.connect(self.showItemsInStatusBar)
        self.addCurrentEditorWidgetChangedListener(self.sceneItemsTableWidget.update)

        self.sceneItemsDock = QDockWidget("Scene items")
        self.sceneItemsDock.setWidget(self.sceneItemsTableWidget)
        self.sceneItemsDock.setFloating(False)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.sceneItemsDock)
        self.sceneItemsDock.hide()

    # noinspection PyAttributeOutsideInit
    def createSceneItemsTreeDock(self) -> None:
        """
        Create scene items tree dock.
        """
        self.sceneItemsTreeWidget = SceneItemsTreeWidget(self)
        self.sceneItemsTreeWidget.itemsPressed.connect(self.showItemsInStatusBar)
        self.addCurrentEditorWidgetChangedListener(self.sceneItemsTreeWidget.update)

        self.sceneItemsTreeDock = QDockWidget("Model tree")
        self.sceneItemsTreeDock.setWidget(self.sceneItemsTreeWidget)
        self.sceneItemsTreeDock.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.sceneItemsTreeDock)

    # noinspection PyAttributeOutsideInit
    def createPythonConsole(self) -> None:
        """
        Create a python console embedded in a dock.
        :return: ``None``
        """
        self.pythonConsoleWidget = ConsoleWidget()
        # self.pythonConsoleWidget.eval_in_thread()

        self.pythonConsoleDock = QDockWidget("Python console")
        self.pythonConsoleDock.setWidget(self.pythonConsoleWidget)
        self.pythonConsoleDock.setFloating(False)

        self.addDockWidget(Qt.BottomDockWidgetArea, self.pythonConsoleDock)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Qt close event handle.

        :param event: close event
        :type event: ``QCloseEvent.py``
        :return: ``None``
        """
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            # self.pythonConsoleWidget.close()
            event.accept()

    def newFile(self) -> QMdiSubWindow:
        """
        New file.

        Create a new sub window and show it.

        :return: ``None``
        """
        subWindow = self._createMdiSubWindow()
        # cast(EditorWidget, subWindow.widget()).addNodes()
        subWindow.show()

        return subWindow

    def openFile(self, filenames: Any) -> None:
        """
        Open fileS.
        TODO: Rename openFile function as it can open several files.


        :param filenames: TODO
        :type filenames: Optional[bool, str, List[str]]
        :return: ``None``
        """
        logger.info(f"Opening {filenames} in Nodedge.")
        if isinstance(filenames, bool) or filenames is None:
            filenames, ok = QFileDialog.getOpenFileNames(
                parent=self,
                caption="Open model from file",
                dir=EditorWindow.getFileDialogDirectory(),
                filter=EditorWindow.getFileDialogFilter(),
            )
            if not ok:
                return
        else:
            # If only one file is given as input,
            # convert the string in list to let the next for loop work properly.
            if isinstance(filenames, str):
                filenames = [filenames]

        for filename in filenames:
            logger.debug(f"Loading {filename}")
            if filename:
                if not os.path.exists(filename):
                    ok = QMessageBox.warning(
                        self,
                        "File not found",
                        f"File {filename} does not exist. \n"
                        "Do you want to open a new file?",
                        QMessageBox.StandardButton.Ok
                        | QMessageBox.StandardButton.Cancel,
                    )
                    self.removeFromRecentFiles(filename)
                    if ok == QMessageBox.StandardButton.Ok:
                        self.newFile()
                    else:
                        logger.warning(f"File {filename} not found.")
                        continue

                if os.path.isdir(filename):
                    filename, ok = QFileDialog.getOpenFileName(
                        parent=self,
                        caption="Open model from file",
                        dir=filename,
                        filter=EditorWindow.getFileDialogFilter(),
                    )

                existingSubWindow = self.findMdiSubWindow(filename)
                if existingSubWindow:
                    logger.debug("Existing sub window")
                    self.mdiArea.setActiveSubWindow(existingSubWindow)
                else:
                    # Create a new sub window and open the file
                    editor = MdiWidget()
                    if editor.loadFile(filename):
                        logger.debug("Loading success")
                        self.statusBar().showMessage(f"File {filename} loaded.", 5000)
                        editor.updateTitle()
                        subWindow = self._createMdiSubWindow(editor)
                        subWindow.show()
                        # self.sceneItemsTableWidget.update()
                        self.sceneItemsTreeWidget.update()
                    else:
                        logger.debug("Loading fail")
                        editor.close()
            else:
                editor = MdiWidget()
                editor.newFile()
                subWindow = self._createMdiSubWindow(editor)
                subWindow.show()
                # self.sceneItemsTableWidget.update()
                self.sceneItemsTreeWidget.update()

    def about(self) -> None:
        """
        About slot.

        Shows a message box with more information about Nodedge.

        :return: ``None``
        """
        QMessageBox.about(
            self,
            "About Nodedge",
            "Nodedge version: pre-release.\n\n"
            "For further information, please contact admin@nodedge.io.\n\n"
            "© 2020-2023 Nodedge",
        )

    def addCommentElement(self):
        if self.currentEditorWidget is not None:
            scene = self.currentEditorWidget.scene
            scene.addElement()

    def onNodesToolbarTriggered(self) -> None:
        """
        Slot called when the nodes toolbar has been triggered.

        :return: ``None``
        """
        logger.debug("Toolbar triggered")

        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def addCurrentEditorWidgetChangedListener(self, callback) -> None:
        """
        Add a callback to current widget changed listener.

        :param callback:
        :return:
        """
        self.currentEditorWidgetChangedListeners.append(callback)

    def onSubWindowActivated(self) -> None:
        """
        Slot called when a sub window is activated.

        :return: ``None``
        """

        if self.currentEditorWidget is not None:
            self.historyListWidget.history = self.currentEditorWidget.scene.history
            # self.sceneItemsTableWidget.scene = self.currentEditorWidget.scene
            self.sceneItemsTreeWidget.scene = self.currentEditorWidget.scene
            graphicsScene = self.currentEditorWidget.scene.graphicsScene
            graphicsScene.itemsPressed.connect(self.showItemsInStatusBar)
            graphicsScene.mouseMoved.connect(self.updateStatusBar)

        for callback in self.currentEditorWidgetChangedListeners:
            callback()

    def updateStatusBar(self, point: QPointF):
        self.statusMousePos.setText(f"{point.x()}, {point.y()}")

    @Slot(list)
    def showItemsInStatusBar(self, items: List[str]):
        """
        Slot triggered when an item has been selected.
        Shows the class names of the selected items in the status bar.

        :param items: selected items
        :type items: ``List[str]``
        """
        self.statusBar().showMessage(f"Pressed items: {items}")

    def onDebugSwitched(self):
        """Event called when the debug action is triggered."""
        self.debugMode = not self.debugMode
        if self.debugMode:
            logger.debug("Debug mode activated")
            self.statusBar().showMessage("Debug mode activated")
            self.sceneItemsDock.show()
            self.debugAct.setChecked(True)
        else:
            logger.debug("Debug mode deactivated")
            self.statusBar().showMessage("Debug mode deactivated")
            self.sceneItemsDock.hide()
            self.debugAct.setChecked(False)

    @Slot()
    def onShowDialogActions(self):
        logger.info(self.actionsDict)
        dialog = ActionPalette(widgetNames=self.actionsDict)
        dialog.exec()

        actionName = dialog.selectedAction

        if actionName is None:
            return

        self.actionsDict[actionName]["action"].trigger()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.pos()
        self.statusMousePos.setText(f"[{pos.x()}, {pos.y()}]")

        super().mouseMoveEvent(event)

    @Slot()
    def onSceneCoderOutputSocketDisconnect(self) -> None:
        """
        Callback to deal with :class:`~nodedge.scene_coder.SceneCoder` warning.
        :return: ``None``
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setInformativeText("One or more blocks are not connected.")
        msg.setWindowTitle("Coder warning")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()
