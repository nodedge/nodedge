from PySide6.QtCore import QEasingCurve, QPropertyAnimation
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QFrame, QSizePolicy, QSpacerItem, QVBoxLayout

from nodedge.homepage.menu_button import MenuButton

MENU_ITEMS = {
    "Home": "homepage.png",
    # "Search": "search_property.png",
    "Help": "questions.png",
    "Spacer": None,
    "Settings": "settings.png",
    "Account": "login.png",
}

ICON_PATH = "resources/white_icons/"

OPEN_WIDTH = 250


class LeftMenuWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        self.buttons = {}
        for text, iconFile in MENU_ITEMS.items():
            if text == "Spacer":
                spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
                self.layout.addSpacerItem(spacer)
                continue
            iconFile = ICON_PATH + iconFile
            # logger.info(f"Adding menu item: {text} with icon {iconFile}")

            button = MenuButton(self, iconFile, text)
            if text == "Home":
                button.setChecked(True)
            self.layout.addWidget(button)
            self.buttons.update({text: button})

        self.anim = QPropertyAnimation(self, b"minimumWidth")
        self.anim.setDuration(500)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)
        # self.anim.setEasingCurve(QEasingCurve.OutBounce)
        self.closedWidth = 0
        self.openWidth = OPEN_WIDTH
        self.anim.setStartValue(self.closedWidth)
        self.anim.setEndValue(self.openWidth)
        self.setFixedWidth(0)
        self.setMinimumWidth(0)

        self.open = False

        self.setObjectName("leftMenuWidget")

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
