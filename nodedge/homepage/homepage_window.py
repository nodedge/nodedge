import logging
import sys

from PySide6.QtWidgets import QApplication, QMainWindow

from nodedge.homepage.content_widget import SettingsContentWidget
from nodedge.homepage.main_widget import MainWidget
from nodedge.nodedge_settings import NodedgeSettings, NodedgeSettingsManager

logger = logging.getLogger(__name__)


class HomePageWindow(QMainWindow):
    def __init__(self):
        super(HomePageWindow, self).__init__()

        self.setWindowTitle("Nodedge")
        self.nodedgeSettings = NodedgeSettingsManager()

        self.mainWidget = MainWidget()
        settingsContentWidget: SettingsContentWidget = (
            self.mainWidget.mainBodyFrame.centralWidget.stackedWidgets[
                "Settings"
            ].contentWidget
        )
        settingsContentWidget.workspaceChanged.connect(
            self.nodedgeSettings.updateSettings
        )
        self.setCentralWidget(self.mainWidget)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    win = HomePageWindow()
    win.showMaximized()
    sys.exit(app.exec())
