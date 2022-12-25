from asammdf import MDF
from PySide6.QtWidgets import QAbstractItemView, QListWidget


class SignalsListWidget(QListWidget):
    def __init__(self, parent=None, signals=[]):
        super().__init__(parent)

        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.signals = signals
        self.addItems(self.signals)

    def updateList(self, log: MDF):
        signals = list(log.channels_db.keys())
        signals = [c for c in signals if c[0:3] != "CAN"]
        signals = [c for c in signals if c[0:3] != "LIN"]
        signals = [c for c in signals if c != "time"]

        self.signals = signals

        self.clear()
        self.addItems(signals)
