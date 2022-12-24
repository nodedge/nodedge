from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy

from nodedge.homepage.header_button import HeaderButton
from nodedge.homepage.header_menu_button import HeaderMenuButton

HEADER_ITEMS = {
    "Search": "search_property.png",
    "Notifications": "alarm.png",
    "Help": "questions.png",
    "Login": "login.png",
}

ICON_PATH = "resources/white_icons/"


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
        self.datsButton = HeaderButton(self, iconFile="resources/Icon.ico", text="Dats")

        self.leftLayout.addWidget(self.menuButton)
        self.leftLayout.addWidget(self.nodedgeButton)
        self.leftLayout.addWidget(self.datsButton)

        self.rightButtons = []

        for text, iconFile in HEADER_ITEMS.items():
            iconFile = ICON_PATH + iconFile
            # logger.debug(f"Adding header item: {text} with icon {iconFile}")

            button = HeaderButton(self, iconFile=iconFile, text=text)
            self.rightLayout.addWidget(button)
            self.rightButtons.append(button)
        #
        # for button in self.rightButtons:
        #     if button.text == "Login":
        #         button.setObjectName("loginButton")
