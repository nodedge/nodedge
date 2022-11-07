import logging
from typing import Optional

import pandas as pd
from asammdf import MDF
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QMessageBox


class LogsListWidget(QListWidget):
    logSelected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.logs = {}

        self.itemClicked.connect(self.onItemClicked)  # type: ignore

    def addLog(self, filename) -> Optional[MDF]:
        shortname = filename.split("/")[-1]
        extension = shortname.split(".")[-1]
        shortname = shortname.split(".")[0]

        log: MDF
        if extension.lower() == "mf4":
            log = MDF(filename)
        elif extension.lower() == "csv":
            df = pd.read_csv(filename)

            log = MDF()

            log.append(df)
        else:
            logging.warning("Cannot open this extension")
            return None

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
