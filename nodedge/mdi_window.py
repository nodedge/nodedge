import os
import typing

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from nodedge.editor_window import EditorWindow
from nodedge.utils import loadStyleSheets, dumpException
from nodedge.editor_widget import EditorWidget
from nodedge.mdi_sub_window import MdiSubWindow
from nodedge.drag_listbox import DragListbox
from nodedge.blocks.block_config import BLOCKS
import logging

# Images for the dark skin
import nodedge.qss.calculator_dark_resources


class MdiWindow(EditorWindow):
    def __init__(self):
        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)
        super(MdiWindow, self).__init__()
        
    @property
    def currentEditorWidget(self) -> EditorWidget:
        """ we're returning NodeEditorWidget here... """
        activeSubWindow = self.mdiArea.activeSubWindow()
        if activeSubWindow and activeSubWindow.widget and isinstance(activeSubWindow.widget(), (EditorWidget)):
            self.lastActiveEditorWidget = activeSubWindow.widget()
        return typing.cast(EditorWidget, self.lastActiveEditorWidget)

    def initUI(self):
        self.companyName = "Nodedge"
        self.productName = "Nodedge"
        self.icon = QIcon(os.path.join(os.path.dirname(__file__), 'resources/favicon_red_white_bg.png'))
        self.setWindowIcon(self.icon)

        self.styleSheetFilename = os.path.join(os.path.dirname(__file__), "qss/calculator.qss")
        loadStyleSheets(
            # os.path.join(os.path.dirname(__file__), "qss/calculator-dark.qss"),
            self.styleSheetFilename
        )

        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setViewMode(QMdiArea.TabbedView)
        self.mdiArea.setDocumentMode(True)
        self.mdiArea.setTabsClosable(True)
        self.mdiArea.setTabsMovable(True)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)

        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createNodesDock()

        self.createActions()
        self.createMenus()
        # self.createToolBars()
        self.createStatusBar()
        self.updateMenus()


        self.readSettings()

        self.setWindowTitle(self.productName)

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

    # noinspection PyArgumentList
    def createActions(self):
        super().createActions()

        self.closeAct = QAction("Cl&ose", self, statusTip="Close the active window",
                                triggered=self.mdiArea.closeActiveSubWindow)

        self.closeAllAct = QAction("Close &All", self,
                                   statusTip="Close all the windows",
                                   triggered=self.mdiArea.closeAllSubWindows)

        self.tileAct = QAction("&Tile", self, statusTip="Tile the windows",
                               triggered=self.mdiArea.tileSubWindows)

        self.cascadeAct = QAction("&Cascade", self,
                                  statusTip="Cascade the windows",
                                  triggered=self.mdiArea.cascadeSubWindows)

        self.nextAct = QAction("Ne&xt", self, shortcut=QKeySequence.NextChild,
                               statusTip="Move the focus to the next window",
                               triggered=self.mdiArea.activateNextSubWindow)

        self.previousAct = QAction("Pre&vious", self,
                                   shortcut=QKeySequence.PreviousChild,
                                   statusTip="Move the focus to the previous window",
                                   triggered=self.mdiArea.activatePreviousSubWindow)

        self.nodeToolbarAct = QAction("&Node toolbar", self,
                                      shortcut="ctrl+alt+n",
                                      statusTip="Enable/Disable the node toolbar",
                                      triggered=self.onNodesToolbarTriggered)
        self.nodeToolbarAct.setCheckable(True)
        self.nodeToolbarAct.setChecked(self.nodesDock.isVisible())

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QAction("&About", self,
                                statusTip="Show the application's About box",
                                triggered=self.about)

    def createToolBars(self):
        self.fileToolBar = self.addToolBar("File")
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)

        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)

    def createMenus(self):
        super().createMenus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.helpMenu: QMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

        self.editMenu.aboutToShow.connect(self.updateEditMenu)

    def updateMenus(self):
        active = self.currentEditorWidget
        hasMdiChild = active is not None

        self.saveAct.setEnabled(hasMdiChild)
        self.saveAsAct.setEnabled(hasMdiChild)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)

        self.updateEditMenu()

    def updateWindowMenu(self):
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

        windows = self.mdiArea.subWindowList()
        self.separatorAct.setVisible(len(windows) != 0)

        for i, window in enumerate(windows):
            child: EditorWidget = window.widget()

            text = "%d %s" % (i + 1, child.userFriendlyFilename)
            if i < 9:
                text = '&' + text

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child is self.currentEditorWidget)
            action.triggered.connect(self.windowMapper.map)
            self.windowMapper.setMapping(action, window)

    def updateEditMenu(self):
        try:
            # self.__logger.debug("Update edit menu")

            active = self.currentEditorWidget
            hasMdiChild = (active is not None)

            self.pasteAct.setEnabled(hasMdiChild)

            hasSelection = hasMdiChild and active.hasSelectedItems()
            self.cutAct.setEnabled(hasSelection)
            self.copyAct.setEnabled(hasMdiChild and active.hasSelectedItems())
            self.deleteAct.setEnabled(hasMdiChild and active.hasSelectedItems())

            self.undoAct.setEnabled(hasMdiChild and active.canUndo)
            self.redoAct.setEnabled(hasMdiChild and active.canRedo)
        except Exception as e:
            dumpException(e)

    def createMdiSubWindow(self, childWidget=None):
        editor = childWidget if childWidget is not None else MdiSubWindow()
        subWindow = self.mdiArea.addSubWindow(editor)

        icon = QIcon(".")
        subWindow.setWindowIcon(icon)
        editor.scene.history.addHistoryModifiedListener(self.updateEditMenu)
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
            if window.widget().filename == filename:
                return window
        return None

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def createNodesDock(self):
        self.nodesListWidget = DragListbox()

        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.nodesListWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    def newFile(self):
        subWindow = self.createMdiSubWindow()
        typing.cast(EditorWidget, subWindow.widget()).addNodes()
        subWindow.show()

        return subWindow

    def openFile(self, filenames):
        if isinstance(filenames, bool) or filenames is None:
            filenames, filter = QFileDialog.getOpenFileNames(parent=self, caption="Open graph from file")
        else:
            # If only one file is given as input, convert the string in list to let the next for loop work properly.
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
                    editor = MdiSubWindow()
                    if editor.loadFile(filename):
                        self.__logger.debug("Loading success")
                        self.statusBar().showMessage(f"File {filename} loaded.", 5000)
                        editor.updateTitle()
                        subWindow = self.createMdiSubWindow(editor)
                        subWindow.show()
                    else:
                        self.__logger.debug("Loading fail")
                        editor.close()

    def about(self):
        QMessageBox.about(self, "About Nodedge calculator",
                "\"Your assumptions are your windows on the world. \n"
                "Scrub them off every once in a while, or the light won't come in.\" \n "
                "Isaac Asimov.")

    def onNodesToolbarTriggered(self):
        self.__logger.debug("")

        if self.nodesDock.isVisible():
            self.nodesDock.hide()
        else:
            self.nodesDock.show()
