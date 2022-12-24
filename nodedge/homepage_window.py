import logging
import sys

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Signal
from PySide6.QtGui import QIcon, Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.utils import loadStyleSheets

MENU_ITEMS = {
    "Home": "home_page.png",
    "Search": "search_property.png",
    "Help": "questions.png",
    "Spacer": None,
    "Settings": "settings.png",
    "Account": "login.png",
}

ICON_PATH = "resources/white_icons/"

HEADER_ITEMS = {
    "Search": "search_property.png",
    "Notifications": "alarm.png",
    "Help": "questions.png",
    "Login": "login.png",
}

logger = logging.getLogger(__name__)


class HeaderButton(QPushButton):
    switched = Signal(int)

    def __init__(self, parent=None, iconFile=None, text=None):
        super().__init__(parent)
        # self.setFlat(True)
        # self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedWidth(40)
        self.setFixedHeight(40)
        self.text = text

        if text is not None:
            self.setObjectName(f"{text.lower()}Button")

        self.icon = QIcon(iconFile)
        self.setIcon(self.icon)

        self.clicked.connect(self.onClicked)

    def onClicked(self):
        self.switched.emit(0)


class HeaderMenuButton(HeaderButton):
    def __init__(self, parent=None, iconFile=None, text=None, toggleIconFile=None):
        super().__init__(parent, iconFile, text)
        self.setCheckable(True)
        self.setFlat(True)
        self.toggled.connect(self.onToggled)

        self.toggleIcon = QIcon(toggleIconFile)

    def onToggled(self, checked):
        self.setChecked(checked)
        # if checked:
        #     self.setIcon(self.toggleIcon)
        # else:
        #     self.setIcon(self.icon)


class MenuButton(QPushButton):
    def __init__(self, parent=None, icon=None, text=None):
        super().__init__(parent, text=text)
        self.setCheckable(True)
        self.setFlat(True)
        self.setObjectName(f"{text.lower()}MenuButton")

        # if isinstance(icon, str):
        #     icon = QIcon(icon)
        # icon = QIcon(icon)
        # self.setIcon(icon)

        self.setFixedHeight(40)

        cursor = Qt.PointingHandCursor
        self.setCursor(cursor)

        self.toggled.connect(self.onToggled)

    def onToggled(self, checked):
        self.setChecked(checked)
        # if checked:
        #     darkColor = QApplication.palette().dark().color().name()
        #     self.setStyleSheet(f"background-color: {darkColor};")
        # else:
        #     self.setStyleSheet(f"")


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

        self.menuButton = HeaderMenuButton(
            self,
            iconFile="resources/white_icons/menu.png",
            toggleIconFile="resources/white_icons/chevron_left.png",
        )

        self.nodedgeButton = HeaderButton(self, iconFile="resources/Icon.ico")

        self.leftLayout.addWidget(self.menuButton)
        self.leftLayout.addWidget(self.nodedgeButton)

        self.rightButtons = []

        for text, iconFile in HEADER_ITEMS.items():
            iconFile = ICON_PATH + iconFile
            logger.debug(f"Adding header item: {text} with icon {iconFile}")

            button = HeaderButton(self, iconFile=iconFile, text=text)
            self.rightLayout.addWidget(button)
            self.rightButtons.append(button)
        #
        # for button in self.rightButtons:
        #     if button.text == "Login":
        #         button.setObjectName("loginButton")


class LeftMenuWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.buttons = []
        for text, iconFile in MENU_ITEMS.items():
            if text == "Spacer":
                spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
                self.layout.addSpacerItem(spacer)
                continue
            iconFile = ICON_PATH + iconFile
            logger.info(f"Adding menu item: {text} with icon {iconFile}")

            button = MenuButton(self, iconFile, text)
            if text == "Home":
                button.setChecked(True)
            self.layout.addWidget(button)
            self.buttons.append(button)

        # self.
        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)
        # self.anim.setEasingCurve(QEasingCurve.OutBounce)
        self.closedWidth = 0
        self.openWidth = 200
        self.anim.setStartValue(self.closedWidth)
        self.anim.setEndValue(self.openWidth)
        self.setFixedWidth(0)

        self.open = False

    def toggle(self):
        if self.open:
            self.open = False
            self.anim.setStartValue(self.openWidth)
            self.anim.setEndValue(self.closedWidth)
        else:
            self.open = True
            self.anim.setStartValue(self.closedWidth)
            self.anim.setEndValue(self.openWidth)

        self.anim.start()


class ContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class SettingsContentWidget(ContentWidget):

    paletteChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QFormLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        # self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.paletteCombo = QComboBox()
        self.paletteCombo.addItems(["Dark", "Light"])
        self.layout.addRow("Theme: ", self.paletteCombo)

        self.styler = ApplicationStyler()
        self.paletteCombo.currentTextChanged.connect(self.onPaletteChanged)

    def onPaletteChanged(self, text):
        self.styler.setCustomPalette(text)
        p = QApplication.palette()

        loadStyleSheets(
            # os.path.join(os.path.dirname(__file__), "qss/calculator-dark.qss"),
            self.styler.styleSheetFilename
        )

        self.paletteChanged.emit()


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QStackedLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.stackedWidgets = {}
        for text, iconFile in MENU_ITEMS.items():
            if text == "Settings":
                stackedWidget = StackedWidget(
                    self, text, contentWidget=SettingsContentWidget()
                )
            else:
                stackedWidget = StackedWidget(self, text)
            self.layout.addWidget(stackedWidget)
            self.stackedWidgets.update({text: stackedWidget})


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


class TitleLabel(QLabel):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)
        self.setText(text)
        self.setMaximumHeight(50)
        self.setAlignment(Qt.AlignCenter)


class ContentLabel(QLabel):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)


class StackedWidget(QWidget):
    def __init__(self, parent=None, title=None, contentWidget=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        if title is None:
            title = "Untitled"
        self.titleLabel = TitleLabel(self, title)
        self.titleLabel.setMaximumHeight(50)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        if contentWidget is None:
            self.contentWidget = ContentLabel(self, "No content")
            self.contentWidget.setAlignment(Qt.AlignCenter)

        else:
            self.contentWidget = contentWidget

        self.layout.addWidget(self.titleLabel, Qt.AlignTop)
        self.layout.addWidget(self.contentWidget)


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
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
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

        for button in self.mainBodyFrame.leftMenuWidget.buttons:
            button.clicked.connect(self.updateCentralWidget)

    def updateLeftMenu(self):
        self.mainBodyFrame.leftMenuWidget.toggle()

    def updateCentralWidget(self):
        senderText = self.sender().text()
        try:
            for button in self.mainBodyFrame.leftMenuWidget.buttons:
                if button.text() == senderText:
                    button.setChecked(True)
                else:
                    button.setChecked(False)
            self.mainBodyFrame.centralWidget.layout.setCurrentWidget(
                self.mainBodyFrame.centralWidget.stackedWidgets[self.sender().text()]
            )
        except KeyError:
            logger.error(f"KeyError: {senderText} not found in stackedWidgets")


class HomePageWindow(QMainWindow):
    def __init__(self):
        super(HomePageWindow, self).__init__()

        self.setWindowTitle("Nodedge")

        self.mainWidget = MainWidget()
        self.setCentralWidget(self.mainWidget)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    styler = ApplicationStyler()
    win = HomePageWindow()
    win.showMaximized()
    sys.exit(app.exec())
