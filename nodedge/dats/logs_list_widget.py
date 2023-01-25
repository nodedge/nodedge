import datetime
import logging
import os
from typing import Callable, Optional, Union

import nptdms
import numpy as np
import pandas as pd
from asammdf import MDF
from asammdf import Signal as asammdfSignal
from PySide6.QtCore import QEvent, Signal
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QInputDialog,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
)
from scipy.io import loadmat

DUMMY_CHAR = ["'", "\\", "[", "]", "(", ")"]
SEPARATORS = ["-", "+", "*", ".", "/", " "]


class LogsListWidget(QListWidget):
    logSelected = Signal(object)

    def __init__(self, parent=None, logs={}):
        super().__init__(parent)

        self.logs = {}
        self.addLogs(logs, prependDate=False)

        self.itemClicked.connect(self.onItemClicked)
        self.installEventFilter(self)

        self.closeAct = self.createAction(
            "Close log",
            self.closeLog,
            "Close the selected log",
        )

    def closeLog(self):
        item = self.currentItem()
        if item is not None:
            self.takeItem(self.row(item))
            del self.logs[item.text()]
            self.logSelected.emit(None)

    def createAction(
        self,
        name: str,
        callback: Callable,
        statusTip: Optional[str] = None,
        shortcut: Union[None, str, QKeySequence] = None,
    ) -> QAction:
        """
        Create an action for this window and add it to actions list.

        :param name: action's name
        :type name: ``str``
        :param callback: function to be called when the action is triggered
        :type callback: ``Callable``
        :param statusTip: Description of the action displayed
            at the bottom left of the application.
        :type statusTip: Optional[``str``]
        :param shortcut: Keyboard shortcut to trigger the action.
        :type shortcut: ``Optional[str]``
        :return:
        """
        act = QAction(name, self)
        act.triggered.connect(callback)  # type: ignore

        if statusTip is not None:
            act.setStatusTip(statusTip)
            act.setToolTip(statusTip)

        if shortcut is not None:
            act.setShortcut(QKeySequence(shortcut))

        self.addAction(act)

        return act

    def openLog(self, filename) -> Optional[MDF]:
        shortname = filename.split("/")[-1]
        shortname, extension = split_filename(shortname)

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
            log.start_time = get_creation_date(filename)
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
            log.start_time = get_creation_date(filename)
            log.append(signals)

        elif extension.lower() == "tdms":
            tdmsFile = nptdms.TdmsFile(filename)

            # Convert file to dataframe and rename columns
            df = tdmsFile.as_dataframe()
            refactor_string = lambda text: replace_separators_in_string(
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
            log.start_time = get_creation_date(filename)
            log.append(signals)

        else:
            logging.warning("Cannot open this extension")
            return None

        self.addLog(log, shortname)

        return log

    def addLog(self, log, shortname, prependDate=True):
        startTimeStr = ""
        if prependDate:
            startTimeStr = log.start_time.strftime("%Y/%m/%d, %H:%M:%S")
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

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self:
            item = source.itemAt(event.pos())
            if item is not None:
                menu = QMenu()
                menu.addAction(self.closeAct)
                menu.exec(event.globalPos())

            return True
        return super().eventFilter(source, event)


def remove_dummy_char_from_string(string, dummy_char=DUMMY_CHAR):
    """
    Removes all dummy characters from a string.
    """
    for c in dummy_char:
        string = string.replace(c, "")

    return string


def replace_separators_in_string(string, sep=SEPARATORS):
    for s in sep:
        string = string.replace(s, "_")
        if len(string) > 0 and string[0] == "_":
            string = string[1:]
    return string


def split_filename(input_string):
    """
    Splits a filename in name and extension.
    """
    dot_index = input_string.rfind(".")
    if dot_index == -1:
        filename = input_string
        extension = ""
    else:
        filename = input_string[:dot_index]
        extension = input_string[dot_index + 1 :]
    return filename, extension


def get_creation_date(file_path):
    """
    Returns the date of creation of the file in the datetime format.
    """
    if os.name == "nt":
        return datetime.datetime.fromtimestamp(os.path.getctime(file_path))
    else:
        stat = os.stat(file_path)
        try:
            return datetime.datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return datetime.datetime.fromtimestamp(stat.st_mtime)
