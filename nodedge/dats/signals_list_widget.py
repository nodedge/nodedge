from asammdf import MDF
from PySide6.QtWidgets import QAbstractItemView, QListWidget


class SignalsListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

    def updateList(self, mdfFile: MDF):
        channels = list(mdfFile.channels_db.keys())
        # channels = [c for c in channels if c[0:3]!="CAN"]

        self.clear()
        self.addItems(channels)
