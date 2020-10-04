# -*- coding: utf-8 -*-
"""
Log analyzer module containing LogAnalyzer class.
"""
import logging
import os

from PySide2.QtWidgets import QFileDialog, QMainWindow, QMenu, QPlainTextEdit


class MainWindow(QMainWindow):
    """
    MainWindow containing the analysis of the logs.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.textEdit = QPlainTextEdit()
        self.curFile = ""

        logging.basicConfig(
            format="%(asctime)s|%(created)f|%(levelname).4s|%(filename)-15.15s|"
            "%(lineno)-3.3s|%(funcName)-10.10s|%(process)d|%(thread)d|"
            "%(message)s"
        )

        self.createMenus()

    def openFile(self, filename):
        self.__logger.debug("Opening graph")
        if self.maybeSave():
            if filename is None:
                filename, _ = QFileDialog.getOpenFileName(
                    parent=self,
                    caption="Open graph from file",
                    dir=MainWindow.getFileDialogDirectory(),
                    filter=MainWindow.getFileDialogFilter(),
                )

            if filename == "":
                return
            if os.path.isfile(filename):
                self.currentEditorWidget.loadFile(filename)
                self.statusBar().showMessage(
                    f"Successfully opened {os.path.basename(filename)}", 5000
                )

                self.updateTitle()

    def createMenus(self):
        self.createFileMenu()

    # noinspection PyAttributeOutsideInit
    def createFileMenu(self):
        self.fileMenu: QMenu = self.menuBar().addMenu("&File")

    @staticmethod
    def getFileDialogDirectory() -> str:
        """
        Returns starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        return "../../log"

    @staticmethod
    def getFileDialogFilter() -> str:
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "Log (*.log);CSV (*.csv);All files (*)"
