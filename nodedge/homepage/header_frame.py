from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy

from nodedge.homepage.header_button import (
    HeaderIconButton,
    HeaderMenuIconButton,
    HeaderTextButton,
)

HEADER_ITEMS = {
    "Sign In": "text",
    "Sign Up": "text",
    "Login": "icon",
}


class HeaderFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(50)
        self.setFixedHeight(65)

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

        self.menuButton = HeaderMenuIconButton(
            self,
            iconFile="resources/white_icons/menu.png",
            toggleIconFile="resources/white_icons/chevron_left.png",
        )

        self.nodedgeButton = HeaderIconButton(self, text="Nodedge")
        self.datsButton = HeaderIconButton(
            self, iconFile="resources/white_icons/line_chart.png", text="Dats"
        )

        self.leftLayout.addWidget(self.menuButton)
        self.leftLayout.addWidget(self.nodedgeButton)
        self.leftLayout.addWidget(self.datsButton)

        self.rightButtons = {}

        for buttonName, buttonType in HEADER_ITEMS.items():

            if buttonType == "text":
                button = HeaderTextButton(self, text=buttonName)
            else:
                button = HeaderIconButton(self, text=buttonName)
            self.rightLayout.addWidget(button)
            self.rightButtons.update({buttonName: button})

        self.rightButtons["Sign In"].clicked.connect(self.signIn)
        self.rightButtons["Login"].hide()

        #
        # for button in self.rightButtons:
        #     if button.text == "Login":
        #         button.setObjectName("loginButton")

    def signIn(self):
        self.rightButtons["Sign In"].setText("Sign Out")
        self.rightButtons["Sign In"].clicked.disconnect(self.signIn)
        self.rightButtons["Sign In"].clicked.connect(self.signOut)
        self.rightButtons["Sign Up"].hide()
        self.rightButtons["Login"].show()

    def signOut(self):
        self.rightButtons["Sign In"].setText("Sign In")
        self.rightButtons["Sign In"].clicked.disconnect(self.signOut)
        self.rightButtons["Sign In"].clicked.connect(self.signIn)
        self.rightButtons["Sign Up"].show()
        self.rightButtons["Login"].hide()
