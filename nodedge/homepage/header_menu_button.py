from PySide6.QtGui import QIcon

from nodedge.homepage.header_button import HeaderButton


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
