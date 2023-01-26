import logging

from PySide6.QtWidgets import QVBoxLayout, QWidget

from nodedge.homepage.header_frame import HeaderFrame
from nodedge.homepage.main_body_frame import MainBodyFrame

logger = logging.getLogger(__name__)


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
        self.headerFrame.menuButton.click()

        for text, button in self.mainBodyFrame.leftMenuWidget.buttons.items():
            button.clicked.connect(self.updateCentralWidget)

    def updateLeftMenu(self):
        self.mainBodyFrame.leftMenuWidget.toggle()

    def updateCentralWidget(self):
        senderText = self.sender().text()
        try:
            for text, button in self.mainBodyFrame.leftMenuWidget.buttons.items():
                if text == senderText:
                    button.setChecked(True)
                else:
                    button.setChecked(False)
            self.mainBodyFrame.centralWidget.layout.setCurrentWidget(
                self.mainBodyFrame.centralWidget.stackedWidgets[self.sender().text()]
            )
        except KeyError:
            logger.error(f"KeyError: {senderText} not found in stackedWidgets")
