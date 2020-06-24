# -*- coding: utf-8 -*-
"""Multi Document Interface window module containing
:class:`~nodedge.mdi_window.MdiWindow` class. """
import logging
import os
from typing import List, cast

from PyQt5.QtCore import QFile, QSignalMapper, Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QCursor, QIcon, QKeySequence, QPalette
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDockWidget,
    QFileDialog,
    QHeaderView,
    QMainWindow,
    QMdiArea,
    QMenu,
    QMessageBox,
    QVBoxLayout,
    QWidget,
    qApp,
)

from nodedge.editor_widget import EditorWidget
from nodedge.editor_window import EditorWindow
from nodedge.history_list_widget import HistoryListWidget
from nodedge.mdi_area import MdiArea
from nodedge.mdi_widget import MdiWidget
from nodedge.node_list_widget import NodeListWidget
from nodedge.scene_items_table_widget import SceneItemsTableWidget
from nodedge.utils import dumpException, loadStyleSheets, widgetsAt


class MdiWindow(EditorWindow):
    """
    :class:`~nodedge.mdi_window.MdiWindow` class.

    The mdi window is the main window of Nodedge.
    """

    def __init__(self):
        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.currentEditorWidgetChangedListeners = []

        self.stylesheetLastModified = 0

        super(MdiWindow, self).__init__()

    @property
    def currentEditorWidget(self) -> EditorWidget:
        """
        Property representing the :class:`~nodedge.editor_widget.EditorWidget` of the
        active sub-window.

        .. note::

            This property cannot be set.

        :type: :class:`~nodedge.editor_widget.EditorWidget`
        """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if (
            activeSubWindow
            and activeSubWindow.widget
            and isinstance(activeSubWindow.widget(), EditorWidget)
        ):
            self.lastActiveEditorWidget = activeSubWindow.widget()
        return cast(EditorWidget, self.lastActiveEditorWidget)

    # noinspection PyAttributeOutsideInit
    def initUI(self):
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
        self.timer.setInterval(500.0)
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
        # noinspection PyUnresolvedReferences
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

    def createStatusBar(self):
        """
        Create the status bar describing Nodedge status and the mouse position.
        """
        self.statusBar().showMessage("Ready")

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createActions(self):
        """
        Create `File`, `Edit` and `About` actions.
        """
        super().createActions()

        self.closeAct = QAction(
            "Cl&ose",
            self,
            statusTip="Close the active window",
            triggered=self.mdiArea.closeActiveSubWindow,
        )

        self.closeAllAct = QAction(
            "Close &All",
            self,
            statusTip="Close all the windows",
            triggered=self.mdiArea.closeAllSubWindows,
        )

        self.tileAct = QAction(
            "&Tile",
            self,
            statusTip="Tile the windows",
            triggered=self.mdiArea.tileSubWindows,
        )

        self.cascadeAct = QAction(
            "&Cascade",
            self,
            statusTip="Cascade the windows",
            triggered=self.mdiArea.cascadeSubWindows,
        )

        self.nextAct = QAction(
            "Ne&xt",
            self,
            shortcut=QKeySequence.NextChild,
            statusTip="Move the focus to the next window",
            triggered=self.mdiArea.activateNextSubWindow,
        )

        self.previousAct = QAction(
            "Pre&vious",
            self,
            shortcut=QKeySequence.PreviousChild,
            statusTip="Move the focus to the previous window",
            triggered=self.mdiArea.activatePreviousSubWindow,
        )

        self.nodeToolbarAct = QAction(
            "&Node toolbar",
            self,
            shortcut="ctrl+alt+n",
            statusTip="Enable/Disable the node toolbar",
            triggered=self.onNodesToolbarTriggered,
        )
        self.nodeToolbarAct.setCheckable(True)
        self.nodeToolbarAct.setChecked(True)  # self.nodesDock.isVisible()

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QAction(
            "&About",
            self,
            statusTip="Show the application's About box",
            triggered=self.about,
        )

    # noinspection PyAttributeOutsideInit
    def createToolBars(self):
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

    def createMenus(self):
        """
        Create `Window` and `Help` menus.

        `Window` menu allows to navigate between the sub-windows.
        `Help` menu allows to display know more about Nodedge.
        """
        super().createMenus()

        self.createWindowMenu()
        self.createHelpMenu()

        self.editMenu.aboutToShow.connect(self.updateEditMenu)

    # noinspection PyAttributeOutsideInit
    def createHelpMenu(self):
        self.helpMenu: QMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

    # noinspection PyAttributeOutsideInit
    def createWindowMenu(self):
        self.windowMenu = self.menuBar().addMenu("&Window")
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

    def updateMenus(self):
        """
        Update menus accordingly to the presence or not of sub-window in the editor,
        enabling and disabling file manipulation actions, for example.
        """

        self.updateFileMenu()
        self.updateEditMenu()
        self.updateWindowMenu()

    def updateFileMenu(self):
        """
        Update file menu.
        """
        active = self.currentEditorWidget
        hasMdiChild = active is not None
        self.saveAct.setEnabled(hasMdiChild)
        self.saveAsAct.setEnabled(hasMdiChild)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)

    def updateWindowMenu(self):
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
            child: EditorWidget = window.widget()

            text = "%d %s" % (i + 1, child.userFriendlyFilename)
            if i < 9:
                text = "&" + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.currentEditorWidget)
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def updateEditMenu(self):
        """
        Update edit menu.
        """
        try:
            # self.__logger.debug("Update edit menu")

            active = self.currentEditorWidget
            hasMdiChild = active is not None

            self.pasteAct.setEnabled(hasMdiChild)

            hasSelection = hasMdiChild and active.hasSelectedItems
            self.cutAct.setEnabled(hasSelection)
            self.copyAct.setEnabled(hasMdiChild and active.hasSelectedItems)
            self.deleteAct.setEnabled(hasMdiChild and active.hasSelectedItems)

            self.undoAct.setEnabled(hasMdiChild and active.canUndo)
            self.redoAct.setEnabled(hasMdiChild and active.canRedo)
        except Exception as e:
            dumpException(e)

    def _createMdiSubWindow(self, childWidget=None):
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

    def onSubWindowClosed(self, widget, event):
        subWindowToBeDeleted = self.findMdiSubWindow(widget.filename)
        self.mdiArea.setActiveSubWindow(subWindowToBeDeleted)

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def findMdiSubWindow(self, filename):
        for window in self.mdiArea.subWindowList():
            editorWidget: EditorWidget = cast(EditorWidget, window.widget())
            if editorWidget.filename == filename:
                return window
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    # noinspection PyAttributeOutsideInit
    def createNodesDock(self):
        self.nodesListWidget = NodeListWidget()
        self.nodesListWidget.itemsPressed.connect(self.showItemsInStatusBar)

        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.nodesListWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)

    # noinspection PyAttributeOutsideInit
    def createHistoryDock(self):
        self.historyListWidget = HistoryListWidget(self)
        self.historyListWidget.itemsPressed.connect(self.showItemsInStatusBar)
        self.addCurrentEditorWidgetChangedListener(self.historyListWidget.update)

        self.historyDock = QDockWidget("History")
        self.historyDock.setWidget(self.historyListWidget)
        self.historyDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.historyDock)

    # noinspection PyAttributeOutsideInit
    def createSceneItemsDock(self):
        self.sceneItemsTableWidget = SceneItemsTableWidget(self)
        self.sceneItemsTableWidget.itemsPressed.connect(self.showItemsInStatusBar)
        self.addCurrentEditorWidgetChangedListener(self.sceneItemsTableWidget.update)

        self.sceneItemsDock = QDockWidget("Scene items")
        self.sceneItemsDock.setWidget(self.sceneItemsTableWidget)
        self.sceneItemsDock.setFloating(False)

        self.addDockWidget(Qt.LeftDockWidgetArea, self.sceneItemsDock)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def newFile(self):
        subWindow = self._createMdiSubWindow()
        # cast(EditorWidget, subWindow.widget()).addNodes()
        subWindow.show()

        return subWindow

    def openFile(self, filenames):
        if isinstance(filenames, bool) or filenames is None:
            filenames, _ = QFileDialog.getOpenFileNames(
                parent=self,
                caption="Open graph from file",
                directory=EditorWindow.getFileDialogDirectory(),
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
                    self.__logger.debug("Existing subwindow")
                    self.mdiArea.setActiveSubWindow(existingSubWindow)
                else:
                    # Create a new subwindow and open the file
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

    def about(self):
        QMessageBox.about(
            self,
            "About Nodedge calculator",
            '"Your assumptions are your windows on the world. \n'
            "Scrub them off every once in a while, or the light won't come in.\" \n "
            "Isaac Asimov.",
        )

    def onNodesToolbarTriggered(self):
        self.__logger.debug("Toolbar triggered")

        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()

    def addCurrentEditorWidgetChangedListener(self, callback):
        self.currentEditorWidgetChangedListeners.append(callback)

    def onSubWindowActivated(self):
        for callback in self.currentEditorWidgetChangedListeners:
            callback()

        if (
            self.currentEditorWidget is not None
            and self.currentEditorWidget.scene is not None
            and self.currentEditorWidget.scene.history is not None
        ):
            self.historyListWidget.history = self.currentEditorWidget.scene.history
            self.sceneItemsTableWidget.scene = self.currentEditorWidget.scene
            self.currentEditorWidget.scene.graphicsScene.itemsPressed.connect(
                self.showItemsInStatusBar
            )
            # self.currentEditorWidget.scene.graphicsScene.itemSelected.connect(
            #     self.sceneItemsTableWidget.onSceneItemSelected
            # )

    def checkStylesheet(self):
        try:
            modTime = os.path.getmtime(self.styleSheetFilename)
        except FileNotFoundError:
            self.__logger.warning("Stylesheet was not found")
            return

        if modTime != self.stylesheetLastModified:
            self.stylesheetLastModified = modTime
            loadStyleSheets(self.styleSheetFilename)

    # def mousePressEvent(self, event):
    #     pos = QCursor.pos()
    #     self.__logger.debug([w.__class__ for w in widgetsAt(pos)])
    #     return super().mousePressEvent(event)

    def showItemsInStatusBar(self, items: List[str]):
        self.statusBar().showMessage(f"Pressed items: {items}")
