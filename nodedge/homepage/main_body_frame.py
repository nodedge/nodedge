from PySide6.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QWidget

from nodedge.homepage.central_widget import CentralWidget
from nodedge.homepage.left_menu_widget import LeftMenuWidget


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
