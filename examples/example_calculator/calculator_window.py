from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from nodedge.ack_editor_window import AckEditorWindow
from nodedge.utils import dumpException
import logging


class CalculatorWindow(AckEditorWindow):
    def __init__(self):
        super(CalculatorWindow, self).__init__()
        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

    def initUI(self):
        self.mdiArea = QMdiArea()
        self.mdiArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdiArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdiArea)

        self.mdiArea.subWindowActivated.connect(self.updateMenus)
        self.windowMapper = QSignalMapper(self)
        self.windowMapper.mapped[QWidget].connect(self.setActiveSubWindow)

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.createNodesDock()

        self.companyName = "Nodedge"
        self.productName = "Calculator"
        self.readSettings()

        self.setWindowTitle("Calculator")

    def createStatusBar(self):
        self.statusBar().showMessage("Ready")

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

        self.separatorAct = QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QAction("&About", self,
                                statusTip="Show the application's About box",
                                triggered=self.about)

    def createMenus(self):
        super().createMenus()

        self.windowMenu = self.menuBar().addMenu("&Window")
        self.updateWindowMenu()
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)

        self.helpMenu: QMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)


    def createToolBars(self):
        pass

    def updateWindowMenu(self):
        self.windowMenu.clear()
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

        # for i, window in enumerate(windows):
        #     child = window.widget()
        #
        #     text = "%d %s" % (i + 1, child.userFriendlyCurrentFile())
        #     if i < 9:
        #         text = '&' + text
        #
        #     action = self.windowMenu.addAction(text)
        #     action.setCheckable(True)
        #     action.setChecked(child is self.activeMdiChild())
        #     action.triggered.connect(self.windowMapper.map)
        #     self.windowMapper.setMapping(action, window)

    def updateMenus(self):
        pass

    def setActiveSubWindow(self, window):
        if window:
            self.mdiArea.setActiveSubWindow(window)

    def about(self):
        QMessageBox.about(self, "About Nodedge calculator",
                "\"Your assumptions are your windows on the world. \n"
                "Scrub them off every once in a while, or the light won't come in.\" \n "
                "Isaac Asimov.")

    def createNodesDock(self):
        self.listWidget = QListWidget()
        self.listWidget.addItem("Add")
        self.listWidget.addItem("Substract")
        self.listWidget.addItem("Multiply")
        self.listWidget.addItem("Dive")

        self.nodesDock = QDockWidget("Nodes")
        self.nodesDock.setWidget(self.listWidget)
        self.nodesDock.setFloating(False)

        self.addDockWidget(Qt.RightDockWidgetArea, self.nodesDock)

    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()
