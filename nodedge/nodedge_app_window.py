import os

from PySide6.QtCore import QEasingCurve
from PySide6.QtGui import QCloseEvent, QIcon, Qt
from PySide6.QtWidgets import QMainWindow

from nodedge.animated_stack_widget import AnimatedStackWidget
from nodedge.dats.dats_window import DatsWindow
from nodedge.homepage.homepage_window import HomePageWindow
from nodedge.mdi_window import MdiWindow


class NodedgeAppWindow(QMainWindow):
    def __init__(self, parent=None):
        super(NodedgeAppWindow, self).__init__(parent)
        self.setWindowTitle("Nodedge")
        icon = QIcon(
            os.path.join(os.path.dirname(__file__), "../resources/nodedge_logo.png")
        )
        self.setWindowIcon(icon)
        self.mainWidget = AnimatedStackWidget()
        self.mainWidget.setTransitionSpeed(1000)
        # self.mainWidget.setTransitionEasingCurve(QEasingCurve.InOutQuart)
        self.mainWidget.setTransitionEasingCurve(QEasingCurve.OutCubic)
        self.mainWidget.setTransitionDirection(Qt.Horizontal)

        self.mainWidget.setSlideTransition(True)
        # self.mainWidget.setFadeTransition(True)
        # self.layout = QStackedLayout()
        # self.mainWidget.setLayout(self.layout)
        # self.widget = QCustomStackedWidget()
        self.setCentralWidget(self.mainWidget)
        # mdiWindow.openFile(
        #     f"{os.path.dirname(__file__)}/../examples/calculator/calculator.json"
        # )

        self.homepageWindow = HomePageWindow()
        self.mainWidget.addWidget(self.homepageWindow)
        self.mdiWindow = MdiWindow()
        self.mainWidget.addWidget(self.mdiWindow)
        self.datsWindow = DatsWindow()
        self.mainWidget.addWidget(self.datsWindow)
        # self.setCentralWidget(self.mainWidget)
        self.homepageWindow.mainWidget.headerFrame.nodedgeButton.clicked.connect(
            lambda: self.mainWidget.setCurrentWidget(self.mdiWindow)
        )
        self.mdiWindow.homeMenu.pressed.connect(
            lambda: self.mainWidget.setCurrentWidget(self.homepageWindow)
        )

        self.mdiWindow.recentFilesUpdated.connect(
            self.homepageWindow.homeContentWidget.updateNodedgeRecentFilesButtons
        )
        self.mdiWindow.recentFilesUpdated.emit(self.mdiWindow.recentFiles)

        def openNodeEdgeFile(text):
            self.mainWidget.setCurrentWidget(self.mdiWindow)
            self.mdiWindow.openFile(text)

        self.homepageWindow.homeContentWidget.nodedgeFileClicked.connect(
            openNodeEdgeFile
        )

        self.datsWindow.recentFilesUpdated.connect(
            self.homepageWindow.homeContentWidget.updateDatsRecentFilesWidget
        )
        self.datsWindow.recentFilesUpdated.emit(self.datsWindow.recentFiles)

        def openDatsFile(text):
            self.mainWidget.setCurrentWidget(self.datsWindow)
            self.datsWindow.openLog(text)

        self.homepageWindow.homeContentWidget.datsFileClicked.connect(openDatsFile)

        self.homepageWindow.mainWidget.headerFrame.datsButton.clicked.connect(
            lambda: self.mainWidget.setCurrentWidget(self.datsWindow)
        )
        self.mdiWindow.homeMenu.pressed.connect(
            lambda: self.mainWidget.setCurrentWidget(self.homepageWindow)
        )

        self.datsWindow.homeMenu.aboutToShow.connect(
            lambda: self.mainWidget.setCurrentWidget(self.homepageWindow)
        )
        self.mainWidget.setCurrentIndex(0)

    def closeEvent(self, event: QCloseEvent) -> None:
        ok = self.mdiWindow.close()
        if not ok:
            event.ignore()
            return
        ok = self.datsWindow.close()
        if not ok:
            event.ignore()
            return
        self.homepageWindow.close()
        event.accept()
