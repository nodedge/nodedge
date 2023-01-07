import logging
from typing import Optional

import nptdms
import numpy as np
import pandas as pd
from asammdf import MDF
from asammdf import Signal as asammdfSignal
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QInputDialog, QListWidget, QListWidgetItem, QMessageBox
from scipy.io import loadmat

DUMMY_CHAR = ["'", "\\", " ", "-", "+", "*"]


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
            df_filtered = df.select_dtypes(exclude=["object"])
            df = df.drop(columns=df.columns.difference(df_filtered.columns))

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
        elif extension.lower() == "mat":
            mat = loadmat(filename)

            keys = [key for key in mat.keys() if "__" not in key]

            signals = []
            for key in keys:
                newCol = np.squeeze(mat[key])
                dim = len(newCol.shape)
                if dim != 1:
                    logging.warning(f"Skipped variable {key} with {dim} dimensions")
                    continue
                timestamps = np.arange(len(newCol))
                newSignal = asammdfSignal(
                    samples=newCol, timestamps=timestamps, name=key
                )
                signals.append(newSignal)
            log = MDF()
            log.append(signals)

        elif extension.lower() == "tdms":
            tdmsFile = nptdms.TdmsFile(filename)

            # Convert file to dataframe and rename columns
            df = tdmsFile.as_dataframe()
            refactor_string = lambda text: remove_slash_from_string(
                remove_dummy_char_from_string(text)
            )
            columns_dict = {column: refactor_string(column) for column in df.keys()}
            df = df.rename(columns=columns_dict)

            keys = df.keys()

            signals = []
            for key in keys:
                newCol = np.squeeze(df[key])
                dim = len(newCol.shape)
                if dim != 1:
                    logging.warning(f"Skipped variable {key} with {dim} dimensions")
                    continue
                timestamps = np.arange(len(newCol))
                newSignal = asammdfSignal(
                    samples=newCol, timestamps=timestamps, name=key
                )
                signals.append(newSignal)
            log = MDF()
            log.append(signals)

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


def remove_dummy_char_from_string(string, dummy_char=DUMMY_CHAR):
    for c in dummy_char:
        string = string.replace(c, "")

    return string


def remove_slash_from_string(string):
    string = string.replace("/", "_")
    return string
