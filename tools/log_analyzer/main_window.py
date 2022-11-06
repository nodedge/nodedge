# -*- coding: utf-8 -*-
"""
Log analyzer module containing LogAnalyzer class.
"""
import logging
import os
import sys
from typing import Callable, Optional, Union, cast

from PySide6.QtCore import QSettings, QSize
from PySide6.QtGui import (
    QAction,
    QCloseEvent,
    QGuiApplication,
    QIcon,
    QKeySequence,
    QMouseEvent,
)
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenu,
    QPlainTextEdit,
    QToolBar,
)

from nodedge.utils import dumpException
from tools.log_analyzer.application_styler import ApplicationStyler


class MainWindow(QMainWindow):
    """
    MainWindow containing the analysis of the logs.
    """

    def __init__(self, parent=None, applicationName: str = "", iconPath=""):
        super().__init__(parent)

        logging.basicConfig(
            format="%(asctime)s|%(created)f|%(levelname).4s|%(filename)-15.15s|"
            "%(lineno)-3.3s|%(funcName)-10.10s|%(process)d|%(thread)d|"
            "%(message)s"
        )

        self.applicationName: str = applicationName
        self.iconPath = iconPath

        self.textEdit = QPlainTextEdit()
        self.curFile = ""

        self.styler: ApplicationStyler = ApplicationStyler()

        self.instance: QGuiApplication = cast(
            QGuiApplication, QGuiApplication.instance()
        )
        self.readSettings()

        self.createActions()
        self.createMenus()

        self.initUI()
        self.setMouseTracking(True)

    # noinspection PyAttributeOutsideInit
    def initUI(self) -> None:
        """
        Set up this ``QMainWindow``.

        Create the mdi area, actions and menus
        """
        self.companyName = "Nodedge"
        self.productName = "Nodedge"
        self.icon = QIcon(os.path.join(os.path.dirname(__file__), self.iconPath))
        self.setWindowIcon(self.icon)
        self.setMinimumSize(QSize(880, 600))

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()

    def sizeHint(self) -> QSize:
        """
        Qt size hint handle.
        TODO: Investigate if we really need to overwrite this method.

        :return: ``None``
        """
        return QSize(800, 600)

    def openFile(self, filename: str):
        raise NotImplementedError

    def saveFile(self):
        raise NotImplementedError

    def saveFileAs(self):
        raise NotImplementedError

    def quit(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError

    def redo(self):
        raise NotImplementedError

    def cut(self):
        raise NotImplementedError

    def copy(self):
        raise NotImplementedError

    def paste(self):
        raise NotImplementedError

    def delete(self):
        raise NotImplementedError

    def about(self):
        raise NotImplementedError

    def newFile(self):
        raise NotImplementedError

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createActions(self) -> None:
        """
        Create basic `File` and `Edit` actions.
        """

        self.newAct = self.createAction(
            "&New", self.newFile, "Create new Nodedge graph", QKeySequence("Ctrl+N")
        )

        self.openAct = self.createAction(
            "&Open", self.openFile, "Open file", QKeySequence("Ctrl+O")
        )

        self.saveAct = self.createAction(
            "&Save", self.saveFile, "Save file", QKeySequence("Ctrl+S")
        )

        self.saveAsAct = self.createAction(
            "Save &As", self.saveFileAs, "Save file as...", QKeySequence("Ctrl+Shift+S")
        )

        self.quitAct = self.createAction(
            "&Quit", self.quit, "Exit application", QKeySequence("Ctrl+Q")
        )

        self.undoAct = self.createAction(
            "&Undo", self.undo, "Undo last operation", QKeySequence("Ctrl+Z")
        )

        self.redoAct = self.createAction(
            "&Redo", self.redo, "Redo last operation", QKeySequence("Ctrl+Shift+Z")
        )

        self.cutAct = self.createAction(
            "C&ut", self.cut, "Cut selected items", QKeySequence("Ctrl+X")
        )

        self.copyAct = self.createAction(
            "&Copy", self.copy, "Copy selected items", QKeySequence("Ctrl+C")
        )

        self.pasteAct = self.createAction(
            "&Paste", self.paste, "Paste selected items", QKeySequence.Paste
        )

        self.deleteAct = self.createAction(
            "&Delete", self.delete, "Delete selected items", QKeySequence("Del")
        )

        self.aboutAct = self.createAction(
            "&About", self.about, "Show the application's About box"
        )

    def createMenus(self):
        self.createFileMenu()
        self.createEditMenu()
        self.createHelpMenu()

    # noinspection PyAttributeOutsideInit
    def createFileMenu(self):
        self.fileMenu: QMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

    # noinspection PyAttributeOutsideInit
    def createEditMenu(self):
        self.editMenu: QMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.deleteAct)

    # noinspection PyAttributeOutsideInit
    def createHelpMenu(self):
        self.helpMenu: QMenu = self.menuBar().addMenu("&Help")
        self.helpMenu.addAction(self.aboutAct)

    # noinspection PyAttributeOutsideInit
    def createToolBars(self) -> None:
        """
        Create the `File` and `Edit` toolbar containing few of their menu actions.
        """
        self.fileToolBar: QToolBar = self.addToolBar("File")
        self.fileToolBar.setMovable(False)
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.addSeparator()

        self.editToolBar = self.addToolBar("Edit")
        self.editToolBar.setMovable(False)
        self.editToolBar.addAction(self.cutAct)
        self.editToolBar.addAction(self.copyAct)
        self.editToolBar.addAction(self.pasteAct)

    def createStatusBar(self) -> None:
        """
        Create the status bar describing Nodedge status and the mouse position.
        """
        self.statusMousePos = QLabel("")
        self.statusBar().addPermanentWidget(self.statusMousePos)
        self.statusBar().showMessage("Ready")

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
            at the bottom left of the :class:`~nodedge.editor_window.EditorWindow`.
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

    def readSettings(self) -> None:
        """
        Read the permanent profile settings for this application.
        """
        if self.applicationName is "":
            return

        settings = QSettings(self.applicationName)
        self.restoreGeometry(settings.value("windowGeometry"))  # type: ignore
        self.debugMode = settings.value("debug", False)

    def writeSettings(self) -> None:
        """
        Write the permanent profile settings for this application.
        """
        if self.applicationName is "":
            return

        settings = QSettings(self.applicationName)
        settings.setValue("debug", self.debugMode)
        settings.setValue("windowGeometry", self.saveGeometry())

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Qt close event handle.

        :param event: close event
        :type event: ``QCloseEvent.py``
        :return: ``None``
        """
        self.writeSettings()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos = event.pos()
        self.statusMousePos.setText(f"[{pos.x()}, {pos.y()}]")

        super().mouseMoveEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.showMaximized()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
