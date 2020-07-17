# -*- coding: utf-8 -*-
"""Multi Document Interface window module containing
:class:`~nodedge.mdi_window.MdiWindow` class. """
import logging
import os
from typing import Any, Callable, List, Optional, cast

from PySide2.QtCore import QSignalMapper, Qt, QTimer, Slot
from PySide2.QtGui import QCloseEvent, QIcon, QKeySequence
from PySide2.QtWidgets import (
    QAction,
    QDockWidget,
    QFileDialog,
    QMdiArea,
    QMdiSubWindow,
    QMenu,
    QMessageBox,
    QWidget,
)

from nodedge.editor_widget import EditorWidget
from nodedge.editor_window import EditorWindow
from nodedge.history_list_widget import HistoryListWidget
from nodedge.mdi_area import MdiArea
from nodedge.mdi_widget import MdiWidget
from nodedge.node_list_widget import NodeListWidget
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
            activeSubWindow is not None  # type: ignore
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

        self.styleSheetFilename = os.path.join(
            os.path.dirname(__file__), "qss/calculator-dark.qss"
        )
        loadStyleSheets(
            # os.path.join(os.path.dirname(__file__), "qss/calculator-dark.qss"),
            self.styleSheetFilename
        )

        self.timer = QTimer()
        self.timer.setTimerType(Qt.PreciseTimer)
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.checkStylesheet)
        self.timer.start()

        self.mdiArea = MdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.addCurrentEditorWidgetChangedListener(self.updateMenus)

        self.mdiArea.subWindowActivated.connect(self.onSubWindowActivated)

        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createNodesDock()
        self.createHistoryDock()
        self.createSceneItemsDock()

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
        self.statusBar().showMessage("Ready")
        super().createStatusBar()

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createActions(self) -> None:
        """
        Create `File`, `Edit` and `About` actions.
        """
        super().createActions()

        self.closeAct = QAction("Cl&ose", self)
        self.closeAct.setStatusTip("Close the active window")
        self.closeAct.triggered.connect(self.mdiArea.closeActiveSubWindow)

        self.closeAllAct = QAction("Close &All", self)
        self.closeAllAct.setStatusTip("Close all the windows")
        self.closeAllAct.triggered.connect(self.mdiArea.closeAllSubWindows)

        self.tileAct = QAction("&Tile", self)
        self.tileAct.setStatusTip("Tile the windows")
        self.tileAct.triggered.connect(self.mdiArea.tileSubWindows)

        self.cascadeAct = QAction("&Cascade", self)
        self.cascadeAct.setStatusTip("Cascade the windows")
        self.cascadeAct.triggered.connect(self.mdiArea.cascadeSubWindows)

        self.nextAct = QAction("Ne&xt", self)
        self.nextAct.setShortcut(QKeySequence.NextChild)
        self.nextAct.setStatusTip("Move the focus to the next window")
        self.nextAct.triggered.connect(self.mdiArea.activateNextSubWindow)

        # noinspection SpellCheckingInspection
        self.previousAct = QAction("Pre&vious", self)
        self.previousAct.setShortcut(QKeySequence.PreviousChild)
        self.previousAct.setStatusTip("Move the focus to the previous window")
        self.previousAct.triggered.connect(self.mdiArea.activatePreviousSubWindow)

        self.nodeToolbarAct = QAction("&Node toolbar", self)
        self.nodeToolbarAct.setShortcut(QKeySequence("ctrl+alt+n"))
        self.nodeToolbarAct.setStatusTip("Enable/Disable the node toolbar")
        self.nodeToolbarAct.triggered.connect(self.onNodesToolbarTriggered)

        self.nodeToolbarAct.setCheckable(True)
        self.nodeToolbarAct.setChecked(True)  # self.nodesDock.isVisible()

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct: QAction = QAction("&About", self)
        self.aboutAct.setStatusTip("Show the application's About box")
        self.aboutAct.triggered.connect(self.about)

        self.debugAct = QAction("&Debug", self)
        self.debugAct.setShortcut(QKeySequence("ctrl+alt+shift+d"))
        self.debugAct.setStatusTip("Enable/Disable the debug mode")
        self.debugAct.triggered.connect(self.onDebugSwitched)

    # noinspection PyAttributeOutsideInit
    def createToolBars(self) -> None:
        """
        Create the `File` and `Edit` toolbar containing few of their menu actions.
        """
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)

        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)

    def createMenus(self) -> None:
        """
        Create `Window` and `Help` menus.

        `Window` menu allows to navigate between the sub-windows.
        `Help` menu allows to display know more about Nodedge.
        """
        super().createMenus()

        self.createWindowMenu()
        self.createHelpMenu()

        # noinspection PyUnresolvedReferences
        self.editMenu.aboutToShow.connect(self.updateEditMenu)

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
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

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
            action.triggered.connect(self.windowMapper.map)
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
        editor = childWidget if childWidget is not None else MdiWidget()
        subWindow = self.mdiArea.addSubWindow(editor)

        icon = QIcon(".")
        subWindow.setWindowIcon(icon)
        editor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
        editor.scene.history.addHistoryModifiedListener(self.historyListWidget.update)
        editor.scene.history.addHistoryModifiedListener(
            self.sceneItemsTableWidget.update
        )
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
                return cast(QMdiSubWindow, window)
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
    def createNodesDock(self) -> None:
        """
        Create Nodes dock.
        """
        self.nodesListWidget = NodeListWidget()
        self.nodesListWidget.itemsPressed.connect(  # type: ignore
            self.showItemsInStatusBar
        )

        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.nodesListWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)

    # noinspection PyAttributeOutsideInit
    def createHistoryDock(self) -> None:
        """
        Create history dock.
        """
        self.historyListWidget = HistoryListWidget(self)
        self.historyListWidget.itemsPressed.connect(  # type: ignore
            self.showItemsInStatusBar
        )
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
        self.sceneItemsTableWidget.itemsPressed.connect(  # type: ignore
            self.showItemsInStatusBar
        )
        self.addCurrentEditorWidgetChangedListener(self.sceneItemsTableWidget.update)

        self.sceneItemsDock = QDockWidget("Scene items")
        self.sceneItemsDock.setWidget(self.sceneItemsTableWidget)
        self.sceneItemsDock.setFloating(False)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.sceneItemsDock)

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Qt's close event handle.

        :param event: close event
        :type event: ``QCloseEvent.py``
        :return: ``None``
        """
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
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
            graphicsScene.itemsPressed.connect(  # type: ignore
                self.showItemsInStatusBar
            )
            # self.currentEditorWidget.scene.graphicsScene.itemSelected.connect(
            #     self.sceneItemsTableWidget.onSceneItemSelected
            # )

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

    @Slot(list)  # type: ignore
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
