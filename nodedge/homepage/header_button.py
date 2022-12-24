from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QSizePolicy


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
