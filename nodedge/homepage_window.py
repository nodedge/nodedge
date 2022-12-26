import sys

from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler


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
            self, iconFile="resources/white_icons/search_property.png"
        )
        self.rightLayout.addWidget(searchButton)

        notificationButton = HeaderButton(
            self, iconFile="resources/white_icons/alarm.png"
        )
        self.rightLayout.addWidget(notificationButton)

        helpButton = HeaderButton(self, iconFile="resources/white_icons/questions.png")
        self.rightLayout.addWidget(helpButton)

        loginButton = HeaderButton(self, iconFile="resources/white_icons/login.png")
        loginButton.setObjectName("loginButton")
        self.rightLayout.addWidget(loginButton)

        self.menuButton = HeaderButton(self, iconFile="resources/white_icons/menu.png")

        self.leftLayout.addWidget(self.menuButton)


class MainBodyFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(50)
        self.leftMenuWidget = QWidget(self)
        self.centralWidget = QWidget(self)
        self.rightMenuWidget = QWidget(self)
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(self.leftMenuWidget)
        self.layout.addWidget(self.centralWidget)
        self.layout.addWidget(self.rightMenuWidget)


class HomePageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.headerFrame = HeaderFrame()
        self.mainBodyFrame = MainBodyFrame()
        self.layout.addWidget(self.headerFrame)
        self.layout.addWidget(self.mainBodyFrame)


class HomePageWindow(QMainWindow):
    def __init__(self):
        super(HomePageWindow, self).__init__()

        self.setWindowTitle("Nodedge")

        self.centralWidget = HomePageWidget()
        self.setCentralWidget(self.centralWidget)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    styler = ApplicationStyler()
    win = HomePageWindow()
    win.showMaximized()
    sys.exit(app.exec())
