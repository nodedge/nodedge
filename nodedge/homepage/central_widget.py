from PySide6.QtWidgets import QSizePolicy, QStackedLayout, QWidget

from nodedge.homepage.content_widget import (
    HelpContentWidget,
    HomeContentWidget,
    SettingsContentWidget,
)
from nodedge.homepage.left_menu_widget import MENU_ITEMS
from nodedge.homepage.stacked_widget import StackedWidget


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
            elif text == "Home":
                stackedWidget = StackedWidget(
                    self, "", contentWidget=HomeContentWidget()
                )
            elif text == "Help":
                stackedWidget = StackedWidget(
                    self, text, contentWidget=HelpContentWidget()
                )
            else:
                stackedWidget = StackedWidget(self, text)
            self.layout.addWidget(stackedWidget)
            self.stackedWidgets.update({text: stackedWidget})
