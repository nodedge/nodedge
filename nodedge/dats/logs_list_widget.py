import logging
from typing import Optional

import pandas as pd
from asammdf import MDF
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QInputDialog, QListWidget, QListWidgetItem, QMessageBox


class LogsListWidget(QListWidget):
    logSelected = Signal(object)

    def __init__(self, parent=None, logs={}):
        super().__init__(parent)

        self.logs = {}
        self.addLogs(logs, prependDate=False)

        self.itemClicked.connect(self.onItemClicked)

    def openLog(self, filename) -> Optional[MDF]:
        shortname = filename.split("/")[-1]
        extension = shortname.split(".")[-1]
        shortname = shortname.split(".")[0]

        log: MDF
        if extension.lower() == "mf4":
            log = MDF(filename)
        elif extension.lower() in ["csv", "txt"]:
            with open(filename, "r") as f:
                line = f.readline()
                separator = ","
                if "," not in line:
                    separator, ok = QInputDialog.getItem(
                        self,
                        "Separator",
                        "Select the separator for the CSV file",
                        [",", ";", "\t"],
                    )

                    if not ok:
                        return None

            df = pd.read_csv(filename, sep=separator)

            log = MDF()

            log.append(df)

        elif extension.lower() == "hdf5":
            raise NotImplementedError("HDF5 not implemented yet")
            # f = h5py.File(filename, "r")
            # allKeys, allTypes, allVariableTypes = getAllKeysHdf5(f)
            # print(allKeys)
            # print(allTypes)
            # print(allVariableTypes)
            #
            # s = {}
            # log = MDF()
            # for key, type, variableType in zip(allKeys, allTypes, allVariableTypes):
            #     if type == H5Types.DATASET:
            #         print(f"{key} {f[key][:]}")
            #         series.update({key: f[key][:]})
            #         df = pd.DataFrame([[f[key][:]]], columns=[key])
            #
            #         log.append(df)

        else:
            logging.warning("Cannot open this extension")
            return None

        self.addLog(log, shortname)

        return log

    def addLog(self, log, shortname, prependDate=True):
        startTimeStr = ""
        if prependDate:
            startTimeStr = log.start_time.strftime("%Y/%m/%D, %H:%M:%S")
            shortname = f"[{startTimeStr}] {shortname}"

        if shortname in list(self.logs.keys()):
            msgBox = QMessageBox()
            msgBox.setText("The log has already been loaded.")
            msgBox.setIcon(QMessageBox.Warning)
            msgBox.exec()
            return log

        self.logs.update({shortname: log})
        item = QListWidgetItem(shortname)
        item.setToolTip(startTimeStr)
        self.addItem(item)

        self.logSelected.emit(log)
        self.setCurrentItem(item)

    def addLogs(self, logs, prependDate=True):
        for logName, log in logs.items():

            self.addLog(log, logName, prependDate)

    def onItemClicked(self, item):
        self.logSelected.emit(self.logs[item.text()])
