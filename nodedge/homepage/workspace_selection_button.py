from PySide6.QtGui import Qt
from PySide6.QtWidgets import QPushButton


class WorkspaceSelectionButton(QPushButton):
    def __init__(self, parent=None, text=None):
        super().__init__(parent, text=text)
        # self.setCheckable(True)
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
