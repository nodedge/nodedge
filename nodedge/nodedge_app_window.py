import os

from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QMainWindow, QStackedLayout, QWidget

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
        self.mainWidget = QWidget()
        self.layout = QStackedLayout()
        self.mainWidget.setLayout(self.layout)
        # mdiWindow.openFile(
        #     f"{os.path.dirname(__file__)}/../examples/calculator/calculator.json"
        # )

        self.mdiWindow = MdiWindow()
        self.layout.addWidget(self.mdiWindow)
        self.homepageWindow = HomePageWindow()
        self.layout.addWidget(self.homepageWindow)
        self.datsWindow = DatsWindow()
        self.layout.addWidget(self.datsWindow)
        self.setCentralWidget(self.mainWidget)
        self.homepageWindow.mainWidget.headerFrame.nodedgeButton.clicked.connect(
            lambda: self.layout.setCurrentWidget(self.mdiWindow)
        )
        self.mdiWindow.homeMenu.aboutToShow.connect(
            lambda: self.layout.setCurrentWidget(self.homepageWindow)
        )

        self.homepageWindow.mainWidget.headerFrame.datsButton.clicked.connect(
            lambda: self.layout.setCurrentWidget(self.datsWindow)
        )
        self.mdiWindow.homeMenu.aboutToShow.connect(
            lambda: self.layout.setCurrentWidget(self.homepageWindow)
        )

        self.datsWindow.homeMenu.aboutToShow.connect(
            lambda: self.layout.setCurrentWidget(self.homepageWindow)
        )
        self.centralWidget().layout().setCurrentIndex(1)

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
