import logging
import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from nodedge.homepage.main_widget import MainWidget

logger = logging.getLogger(__name__)


class HomePageWindow(QMainWindow):
    def __init__(self):
        super(HomePageWindow, self).__init__()

        self.setWindowTitle("Nodedge")

        self.mainWidget = MainWidget()
        self.setCentralWidget(self.mainWidget)

    @property
    def homeContentWidget(self):
        return self.mainWidget.mainBodyFrame.centralWidget.stackedWidgets[
            "Home"
        ].contentWidget

    def showHelp(self):
        self.mainWidget.mainBodyFrame.leftMenuWidget.buttons["Help"].animateClick()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    win = HomePageWindow()
    win.showMaximized()
    sys.exit(app.exec())
