# -*- coding: utf-8 -*-
"""Multi Document Interface window module containing
:class:`~nodedge.mdi_window.MdiWindow` class. """
import logging
import os
from typing import Any, Callable, List, Optional, cast

# from pyqtconsole.console import PythonConsole
from PySide6.QtCore import QSignalMapper, QSize, Qt, QTimer, Slot
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QKeySequence, QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QDockWidget,
    QFileDialog,
    QMdiSubWindow,
    QMenu,
    QMessageBox,
    QToolBar,
    QWidget,
)

from nodedge.editor_widget import EditorWidget
from nodedge.editor_window import EditorWindow
from nodedge.history_list_widget import HistoryListWidget
from nodedge.mdi_area import MdiArea
from nodedge.mdi_widget import MdiWidget
from nodedge.node_tree_widget import NodeTreeWidget
from nodedge.scene_item_detail_widget import SceneItemDetailWidget
from nodedge.scene_items_table_widget import SceneItemsTableWidget
from nodedge.utils import loadStyleSheets


class MdiWindow(EditorWindow):
    """
    :class:`~nodedge.mdi_window.MdiWindow` class.

    The mdi window is the main window of Nodedge.
    """

    def __init__(self) -> None:
        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)
        self.currentEditorWidgetChangedListeners: List[Callable] = []

        self.stylesheetLastModified: float = 0.0

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
            os.path.join(os.path.dirname(__file__), "resources/nodedge_logo.png")
        )
        self.setWindowIcon(self.icon)
        self.setMinimumSize(QSize(880, 600))

        self.styleSheetFilename = os.path.join(
            os.path.dirname(__file__), "qss/nodedge_style.qss"
        )
        loadStyleSheets(
            # os.path.join(os.path.dirname(__file__), "qss/calculator-dark.qss"),
            self.styleSheetFilename
        )

        self.setMouseTracking(True)

        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.checkStylesheet)  # type: ignore
        self.timer.start()

        self.mdiArea = MdiArea()
        self.setCentralWidget(self.mdiArea)

        self.addCurrentEditorWidgetChangedListener(self.updateMenus)

        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)  # type: ignore

        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mappedObject.connect(self.setActiveSubWindow)  # type: ignore

        self.createSceneItemDetailDock()
        self.createNodesDock()
        self.createHistoryDock()
        self.createSceneItemsDock()
        # self.createPythonConsole()

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

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
            "Cl&ose", self.mdiArea.closeActiveSubWindow, "Close the active window"
        )

        self.closeAllAct = self.createAction(
            "Close &All", self.mdiArea.closeAllSubWindows, "Close all the windows"
        )

        self.tileAct = self.createAction(
            "&Tile", self.mdiArea.tileSubWindows, "Tile the windows"
        )

        self.cascadeAct = self.createAction(
            "&Cascade", self.mdiArea.cascadeSubWindows, "Cascade the windows"
        )

        self.hideToolbarAct = self.createAction(
            "Hide toolbars",
            self.hideToolBars,
            "Hide toolbars",
            QKeySequence("Ctrl+T"),
        )

        self.nextAct = self.createAction(
            "Ne&xt",
            self.mdiArea.activateNextSubWindow,
            "Move the focus to the next window",
            QKeySequence.NextChild,
        )

        # noinspection SpellCheckingInspection
        self.previousAct = self.createAction(
            "Pre&vious",
            self.mdiArea.activatePreviousSubWindow,
            "Move the focus to the previous window",
            QKeySequence.PreviousChild,
        )

        self.nodeToolbarAct = self.createAction(
            "&Node toolbar",
            self.onNodesToolbarTriggered,
            "Enable/Disable the node toolbar",
            QKeySequence("ctrl+alt+n"),
        )

        self.nodeToolbarAct.setCheckable(True)
        self.nodeToolbarAct.setChecked(True)  # self.nodesDock.isVisible()

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = self.createAction(
            "&About", self.about, "Show the application's About box"
        )

        self.debugAct = self.createAction(
            "&Debug",
            self.onDebugSwitched,
            "Enable/Disable the debug mode",
            QKeySequence("ctrl+alt+shift+d"),
        )

        self.showDialogActionsAct = self.createAction(
            "Show dialog actions",
            self.onShowDialogActions,
            "Show available actions",
            QKeySequence("ctrl+shift+a"),
        )

        self.addCommentElementAct = self.createAction(
            "Add Comment",
            self.addCommentElement,
            "Add comment element in current scene",
            QKeySequence("Ctrl+Alt+C"),
        )

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
        self.editToolBar.addSeparator()
        self.toolBars.append(self.editToolBar)

        self.coderToolBar = self.addToolBar("Coder")
        self.coderToolBar.addAction(self.generateCodeAct)
        self.coderToolBar.addAction(self.addCommentElementAct)
        self.toolBars.append(self.coderToolBar)

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
        self.createHomeMenu()

        super().createMenus()

        self.createWindowMenu()
        self.createHelpMenu()

        # noinspection PyUnresolvedReferences
        self.editMenu.aboutToShow.connect(self.updateEditMenu)  # type: ignore

    # noinspection PyAttributeOutsideInit
    def createHomeMenu(self):
        self.homeMenu: QMenu = self.menuBar().addMenu(
            QIcon("../../nodedge/resources/iconsModified/home_page_100.png"), "&Home"
        )
        self.homeMenu.aboutToShow.connect(self.openHome)

    def openHome(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setInformativeText("It is not yet implemented.")
        msg.setWindowTitle("Home page")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    # noinspection PyAttributeOutsideInit
    def createHelpMenu(self) -> None:
        """
        Create help menu, containing about action.
        """
        self.helpMenu: QMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

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
                self.__logger.warning(
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
        # self.__logger.debug("Update edit menu")

        active = self.currentEditorWidget
        if active is None:
            return
        hasMdiChild = active is not None

        self.pasteAct.setEnabled(hasMdiChild)

        hasSelection = hasMdiChild and active.hasSelectedItems
        self.cutAct.setEnabled(hasSelection)
        self.copyAct.setEnabled(hasMdiChild and active.hasSelectedItems)
        self.deleteAct.setEnabled(hasMdiChild and active.hasSelectedItems)

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

        icon = QIcon(".")
        subWindow.setWindowIcon(icon)
        editor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        editor.scene.history.addHistoryModifiedListener(self.historyListWidget.update)
        editor.scene.history.addHistoryModifiedListener(
            self.sceneItemsTableWidget.update
        )
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

        self.sceneItemDetailsDock = QDockWidget("Selected node details")
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

        self.nodesDock = QDockWidget("Nodes")
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
        self.sceneItemsTableWidget.itemsPressed.connect(self.showItemsInStatusBar)
        self.addCurrentEditorWidgetChangedListener(self.sceneItemsTableWidget.update)

        self.sceneItemsDock = QDockWidget("Scene items")
        self.sceneItemsDock.setWidget(self.sceneItemsTableWidget)
        self.sceneItemsDock.setFloating(False)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.sceneItemsDock)

    # noinspection PyAttributeOutsideInit
    def createPythonConsole(self) -> None:
        """
        Create a python console embedded in a dock.
        :return: ``None``
        """
        # self.pythonConsoleWidget = PythonConsole(formats=self.styler.consoleStyle)
        # self.pythonConsoleWidget.eval_in_thread()

        # self.pythonConsoleDock = QDockWidget("Python console")
        # self.pythonConsoleDock.setWidget(self.pythonConsoleWidget)
        # self.pythonConsoleDock.setFloating(False)

        # self.addDockWidget(Qt.LeftDockWidgetArea, self.pythonConsoleDock)

        pass

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
        if isinstance(filenames, bool) or filenames is None:
            filenames, _ = QFileDialog.getOpenFileNames(
                parent=self,
                caption="Open graph from file",
                dir=EditorWindow.getFileDialogDirectory(),
                filter=EditorWindow.getFileDialogFilter(),
            )
        else:
            # If only one file is given as input,
            # convert the string in list to let the next for loop work properly.
            if isinstance(filenames, str):
                filenames = [filenames]

        for filename in filenames:
            self.__logger.debug(f"Loading {filename}")
            if filename:
                existingSubWindow = self.findMdiSubWindow(filename)
                if existingSubWindow:
                    self.__logger.debug("Existing sub window")
                    self.mdiArea.setActiveSubWindow(existingSubWindow)
                else:
                    # Create a new sub window and open the file
                    editor = MdiWidget()
                    if editor.loadFile(filename):
                        self.__logger.debug("Loading success")
                        self.statusBar().showMessage(f"File {filename} loaded.", 5000)
                        editor.updateTitle()
                        subWindow = self._createMdiSubWindow(editor)
                        subWindow.show()
                        self.sceneItemsTableWidget.update()
                    else:
                        self.__logger.debug("Loading fail")
                        editor.close()

    def about(self) -> None:
        """
        About slot.

        Shows a message box with more information about Nodedge.

        :return: ``None``
        """
        QMessageBox.about(
            self,
            "About Nodedge calculator",
            '"Your assumptions are your windows on the world. \n'
            "Scrub them off every once in a while, or the light won't come in.\" \n "
            "Isaac Asimov.",
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
        self.__logger.debug("Toolbar triggered")

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
        for callback in self.currentEditorWidgetChangedListeners:
            callback()

        if self.currentEditorWidget is not None:
            self.historyListWidget.history = self.currentEditorWidget.scene.history
            self.sceneItemsTableWidget.scene = self.currentEditorWidget.scene
            graphicsScene = self.currentEditorWidget.scene.graphicsScene
            graphicsScene.itemsPressed.connect(self.showItemsInStatusBar)

    def checkStylesheet(self) -> None:
        """
        Helper function which checks if the stylesheet exists and has changed.
        """
        try:
            modTime = os.path.getmtime(self.styleSheetFilename)
        except FileNotFoundError:
            self.__logger.warning("Stylesheet was not found")
            return

        if modTime != self.stylesheetLastModified:
            self.stylesheetLastModified = modTime
            loadStyleSheets(self.styleSheetFilename)

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
        pass

    @Slot()
    def onShowDialogActions(self):
        self.__logger.info("")
        dialog = QDialog()
        dialog.show()

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
