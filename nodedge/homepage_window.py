import os
import sys

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.utils import loadStyleSheets


class HeaderButton(QPushButton):
    def __init__(self, parent=None, iconFile=None, text=None):
        super().__init__(parent, text=text)
        # self.setFlat(True)
        # self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedWidth(40)
        self.setFixedHeight(40)

        icon = QIcon(iconFile)
        self.setIcon(icon)


class HeaderFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(50)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.leftFrame = QFrame()
        self.leftLayout = QHBoxLayout()
        self.leftFrame.setLayout(self.leftLayout)
        self.leftLayout.setAlignment(Qt.AlignLeft)
        self.layout.addWidget(self.leftFrame)

        self.rightFrame = QFrame()
        self.rightLayout = QHBoxLayout()
        self.rightFrame.setLayout(self.rightLayout)
        self.rightLayout.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.rightFrame)

        searchButton = HeaderButton(
            self, iconFile="resources/white_icons2/search_property.png"
        )
        self.rightLayout.addWidget(searchButton)

        notificationButton = HeaderButton(
            self, iconFile="resources/white_icons2/alarm.png"
        )
        self.rightLayout.addWidget(notificationButton)

        helpButton = HeaderButton(self, iconFile="resources/white_icons2/questions.png")
        self.rightLayout.addWidget(helpButton)

        loginButton = HeaderButton(self, iconFile="resources/white_icons2/login.png")
        loginButton.setObjectName("loginButton")
        self.rightLayout.addWidget(loginButton)

        self.menuButton = HeaderButton(self, iconFile="resources/white_icons2/menu.png")

        self.leftLayout.addWidget(self.menuButton)


class LeftMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)
        self.setStyleSheet("background-color: #2d2d2d;")
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.homeButton = QPushButton(
            self, icon=QIcon("resources/white_icons2/home_page.png"), text="Home"
        )
        self.layout.addWidget(self.homeButton)
        self.settingsButton = QPushButton(
            self, icon=QIcon("resources/white_icons2/settings.png"), text="Settings"
        )
        self.layout.addWidget(self.settingsButton)


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet("background-color: #3d3d3d;")
        self.layout = QStackedLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.homePage = HomePageWidget(self)
        self.layout.addWidget(self.homePage)
        self.settingsWidget = SettingsWidget(self)
        self.layout.addWidget(self.settingsWidget)


class HomePageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.homePageLabel = QLabel("Home Page")
        self.homePageLabel.setMaximumHeight(50)
        self.homePageLabel.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.homePageLabel)


class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.settingsLabel = QLabel("Settings")
        self.settingsLabel.setMaximumHeight(50)
        self.settingsLabel.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.settingsLabel)


class MainBodyFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(50)
        self.leftMenuWidget = LeftMenuWidget(self)
        self.centralWidget = CentralWidget(self)
        self.rightMenuWidget = QWidget(self)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.leftMenuWidget)
        self.layout.addWidget(self.centralWidget)
        self.layout.addWidget(self.rightMenuWidget)


class MainWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.headerFrame = HeaderFrame()
        self.mainBodyFrame = MainBodyFrame()
        self.layout.addWidget(self.headerFrame)
        self.layout.addWidget(self.mainBodyFrame)

        self.headerFrame.menuButton.clicked.connect(self.updateLeftMenu)

        self.mainBodyFrame.leftMenuWidget.homeButton.clicked.connect(
            self.updateCentralWidget
        )
        self.mainBodyFrame.leftMenuWidget.settingsButton.clicked.connect(
            self.updateCentralWidget
        )

    def updateLeftMenu(self):
        print("updateLeftMenu")

    def updateCentralWidget(self):
        senderText = self.sender().text()

        if senderText == "Home":
            self.mainBodyFrame.centralWidget.layout.setCurrentWidget(
                self.mainBodyFrame.centralWidget.homePage
            )
        elif senderText == "Settings":
            self.mainBodyFrame.centralWidget.layout.setCurrentWidget(
                self.mainBodyFrame.centralWidget.settingsWidget
            )


class HomePageWindow(QMainWindow):
    def __init__(self):
        super(HomePageWindow, self).__init__()

        self.setWindowTitle("Nodedge")

        self.mainWidget = MainWidget()
        self.setCentralWidget(self.mainWidget)
        self.styleSheetFilename = os.path.join(
            os.path.dirname(__file__), "../resources/qss/nodedge_style.qss"
        )
        loadStyleSheets(
            # os.path.join(os.path.dirname(__file__), "qss/calculator-dark.qss"),
            self.styleSheetFilename
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)
    styler = ApplicationStyler()
    win = HomePageWindow()
    win.showMaximized()
    sys.exit(app.exec())
