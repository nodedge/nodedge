import logging

from asammdf import MDF
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMessageBox


class LogsListWidget(QListWidget):
    logSelected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.logs = {}

        self.itemClicked.connect(self.onItemClicked)  # type: ignore

    def addLog(self, filename) -> MDF:
        shortname = filename.split("/")[-1]
        extension = shortname.split(".")[-1]
        shortname = shortname.split(".")[0]

        if extension.lower() != "mf4":
            logging.warning("Cannot open this extension")
        log: MDF = MDF(filename)

        startTimeStr = log.start_time.strftime("%Y/%m/%D, %H:%M:%S")
        shortname = f"[{startTimeStr}] {shortname}"

        if shortname in list(self.logs.keys()):
            msgBox = QMessageBox()
            msgBox.setText("The log has already been loaded.")
            msgBox.setIcon(QMessageBox.Warning)  # type: ignore
            msgBox.exec()
            return log

        self.logs.update({shortname: log})
        item = QListWidgetItem(shortname)
        item.setToolTip(startTimeStr)
        self.addItem(item)

        self.logSelected.emit(log)  # type: ignore
        self.setCurrentItem(item)

        return log

    def onItemClicked(self, item):
        self.logSelected.emit(self.logs[item.text()])  # type: ignore
