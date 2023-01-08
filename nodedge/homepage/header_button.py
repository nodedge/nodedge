from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QSizePolicy


class HeaderIconButton(QPushButton):
    def __init__(self, parent=None, iconFile=None, text=None):
        super().__init__(parent)
        # self.setFlat(True)
        # self.setCheckable(True)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedWidth(40)
        self.setFixedHeight(40)
        self.text = text

        if text is not None:
            text = text.lower()
            text = text.replace(" ", "")
            self.setObjectName(f"{text}Button")

        self.icon = QIcon(iconFile)
        self.setIcon(self.icon)


class HeaderTextButton(QPushButton):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)
        self.text = text
        self.setText(self.text)
        self.setCheckable(True)

        if text is not None:
            text = text.lower()
            text = text.replace(" ", "")
            self.setObjectName(f"{text}Button")


class HeaderMenuIconButton(HeaderIconButton):
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
