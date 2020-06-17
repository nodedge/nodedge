# -*- coding: utf-8 -*-
"""
Editor window module containing :class:`~nodedge.editor_window.EditorWindow` class.
"""
import json
import logging
import os
from typing import Optional, cast

from PyQt5.QtCore import QPoint, QSettings, QSize
from PyQt5.QtGui import QClipboard, QCloseEvent, QGuiApplication
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QWidget,
)

from nodedge.editor_widget import EditorWidget


class EditorWindow(QMainWindow):
    """
    :class:`~nodedge.editor_window.EditorWindow` class

    The editor window is the base of the multi document interface (MDI)
    :class:`~nodedge.mdi_window.MdiWindow`.

    The application can be opened with the
    :class:`~nodedge.editor_window.EditorWindow` as main window, even if it is not
    the main use case.
    """

    EditorWidgetClass = EditorWidget

    def __init__(self, parent: Optional[QWidget] = None):
        """
        :Instance Attributes:

        - **name_company** - name of the company, used for permanent profile settings
        - **name_product** - name of this App, used for permanent profile settings
        """

        super().__init__(parent)

        logging.basicConfig(
            format="%(asctime)s|%(levelname).4s|%(filename)10s|"
            "%(lineno).3s|%(message)s|%(funcName)s"
        )

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.companyName = "Nodedge"
        self.productName = "Editor"

        self.instance: QGuiApplication = cast(
            QGuiApplication, QGuiApplication.instance()
        )
        self.clipboard: QClipboard = self.instance.clipboard()

        # Pycharm does not recognise resolve connect method so the inspection is
        # disabled. noinspection PyUnresolvedReferences
        self.clipboard.dataChanged.connect(self.onClipboardChanged)  # type: ignore

        self.lastActiveEditorWidget = None

        self.initUI()

    @property
    def currentEditorWidget(self) -> EditorWidget:
        """
        :getter: Get current :class:`~nodedge.editor_widget.EditorWidget`

        .. note::

            The :class:`~nodedge.editor_window.EditorWindow` has only one
            :class:`~nodedge.editor_widget.EditorWidget`. This method is overridden
            by the :class:`~nodedge.mdi_window.MdiWindow` which may have several
            :class:`~nodedge.editor_widget.EditorWidget`.

        :rtype: :class:`~nodedge.editor_widget`
        """
        centralWidget = self.centralWidget()
        if isinstance(centralWidget, EditorWidget):
            return centralWidget
        else:
            raise TypeError("Central widget is not an editor widget")

    # noinspection PyAttributeOutsideInit
    def initUI(self) -> None:
        """
        Set up this ``QMainWindow``.

        Create :class:`~nodedge.editor_widget.EditorWidget`, Actions and Menus
        """
        self.createActions()

        self.createMenus()

        self.editorWidget = self.__class__.EditorWidgetClass()
        self.setCentralWidget(self.editorWidget)
        self.editorWidget.scene.addHasBeenModifiedListener(self.updateTitle)

        # Initialize status bar
        self.createStatusBar()

        # Set window properties
        # Use sizeHint instead of forced size.
        # self.setGeometry(960, 30, 960, 960)
        self.updateTitle()
        self.show()

    # noinspection PyAttributeOutsideInit
    def createStatusBar(self) -> None:
        """
        Create Status bar and connect to
        :class:`~nodedge.graphics_view.GraphicsView`'s scenePosChanged event.
        """
        self.statusBar().showMessage("")
        self.statusMousePos = QLabel("")
        self.statusBar().addPermanentWidget(self.statusMousePos)
        self.currentEditorWidget.view.scenePosChanged.connect(self.OnScenePosChanged)

    # noinspection PyArgumentList, PyAttributeOutsideInit
    def createActions(self) -> None:
        """
        Create basic `File` and `Edit` actions.
        """
        self.newAct: QAction = QAction("&New", self)
        self.newAct.setShortcut("Ctrl+N")
        self.newAct.setStatusTip("Create new Nodedge graph")
        self.newAct.triggered.connect(self.newFile)

        self.openAct = QAction("&Open", self)
        self.openAct.setShortcut("Ctrl+O")
        self.openAct.setStatusTip("Open file")
        self.openAct.triggered.connect(self.openFile)

        self.saveAct = QAction("&Save", self)
        self.saveAct.setShortcut("Ctrl+S")
        self.saveAct.setStatusTip("Save file")
        self.saveAct.triggered.connect(self.saveFile)

        self.saveAsAct = QAction("Save &As", self)
        self.saveAsAct.setShortcut("Ctrl+Shift+S")
        self.saveAsAct.setStatusTip("Save file as...")
        self.saveAsAct.triggered.connect(self.saveFileAs)

        self.quitAct = QAction("&Quit", self)
        self.quitAct.setShortcut("Ctrl+Q")
        self.quitAct.setStatusTip("Exit application")
        self.quitAct.triggered.connect(self.quit)

        self.undoAct = QAction("&Undo", self)
        self.undoAct.setShortcut("Ctrl+Z")
        self.undoAct.setStatusTip("Undo last operation")
        self.undoAct.triggered.connect(self.undo)

        self.redoAct = QAction("&Redo", self)
        self.redoAct.setShortcut("Ctrl+Shift+Z")
        self.redoAct.setStatusTip("Redo last operation")
        self.redoAct.triggered.connect(self.redo)

        self.cutAct = QAction("C&ut", self)
        self.cutAct.setShortcut("Ctrl+X")
        self.cutAct.setStatusTip("Cut selected items")
        self.cutAct.triggered.connect(self.cut)

        self.copyAct = QAction("&Copy", self)
        self.copyAct.setShortcut("Ctrl+C")
        self.copyAct.setStatusTip("Copy selected items")
        self.copyAct.triggered.connect(self.copy)

        self.pasteAct = QAction("&Paste", self)
        self.pasteAct.setShortcut("Ctrl+V")
        self.pasteAct.setStatusTip("Paste selected items")
        self.pasteAct.triggered.connect(self.paste)

        self.deleteAct = QAction("&Delete", self)
        self.deleteAct.setShortcut("Del")
        self.deleteAct.setStatusTip("Delete selected items")
        self.deleteAct.triggered.connect(self.delete)

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createMenus(self) -> None:
        """
        Create Menus for `File` and `Edit`.
        """
        self.createFileMenu()
        self.createEditMenu()

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createFileMenu(self):
        """
        Create `File` Menu.
        """
        self.fileMenu: QMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createEditMenu(self):
        """
        Create `Edit` Menu.
        """
        self.editMenu: QMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.deleteAct)

    def sizeHint(self):
        return QSize(800, 600)

    def updateTitle(self) -> None:
        """
        Update window title according to the name of the file currently opened.
        """
        if self.currentEditorWidget:
            title = "Create Nodedge"
            if self.currentEditorWidget.hasName:
                title += f" with {self.currentEditorWidget.userFriendlyFilename}"

            else:
                title += "!"

                if self.currentEditorWidget.isModified:
                    title += "*"
            self.setWindowTitle(title)

            self.currentEditorWidget.updateTitle()

    def onClipboardChanged(self) -> None:
        self.__logger.debug(f"Clipboard changed: {self.clipboard.text()}")

    def OnScenePosChanged(self, x: float, y: float):
        """
        Handle event when cursor position changed on the :class:`~nodedge.scene.Scene`.
        :param x: new cursor x position
        :type x: float
        :param y: new cursor y position
        :type y: float
        """

        self.statusMousePos.setText(f"Scene pos: {x}, {y}")

    def newFile(self):
        """
        Open a clean new file in the window's editor.

        Confirmation is asked to the user if there are unsaved changes.
        """
        if self.maybeSave():
            self.__logger.info("Creating new graph")
            self.currentEditorWidget.newFile()
        self.updateTitle()

    def openFile(self, filename):
        """
        Open a file in the window's editor from its filename.

        Confirmation is asked to the user if there are unsaved changes.

        :param filename: absolute path and filename of the file to open.
        :type filename: ``str``
        """
        self.__logger.debug("Opening graph")
        if self.maybeSave():
            if filename is None:
                filename, _ = QFileDialog.getOpenFileName(
                    parent=self,
                    caption="Open graph from file",
                    directory=EditorWindow.getFileDialogDirectory(),
                    filter=EditorWindow.getFileDialogFilter(),
                )

            if filename == "":
                return
            if os.path.isfile(filename):
                self.currentEditorWidget.loadFile(filename)
                self.statusBar().showMessage(
                    f"Successfully opened {os.path.basename(filename)}", 5000
                )

                self.updateTitle()

    def saveFile(self):
        """
        Save serialized JSON version of the currently opened file, in a JSON file
        based on the editor's filename.
        """
        self.__logger.debug("Saving graph")
        if not self.currentEditorWidget.hasName:
            self.saveFileAs()

        self.currentEditorWidget.saveFile(self.currentEditorWidget.filename)
        self.statusBar().showMessage(
            f"Successfully saved to {self.currentEditorWidget.shortName}", 5000
        )
        self.updateTitle()
        self.currentEditorWidget.updateTitle()

    def saveFileAs(self):
        """
        Save serialized JSON version of the currently opened file, allowing the user
        to choose the filename via a ``QFileDialog``.
        """
        self.__logger.debug("Saving graph as...")
        filename, _ = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save graph to file",
            directory=EditorWindow.getFileDialogDirectory(),
            filter=EditorWindow.getFileDialogFilter(),
        )

        if filename == "":
            return

        self.currentEditorWidget.saveFile(filename)
        self.statusBar().showMessage(
            f"Successfully saved to {self.currentEditorWidget.shortName}", 5000
        )
        self.updateTitle()

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Close the window.

        Confirmation is asked to the user if there are unsaved changes.
        """
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def quit(self):
        self.close()

    def undo(self) -> None:
        """
        Undo last operation.
        """
        self.__logger.debug("Undoing last action")
        if self.currentEditorWidget:
            self.currentEditorWidget.scene.history.undo()

    def redo(self) -> None:
        """
        Redo previously cancelled operation.
        """
        self.__logger.debug("Redoing last action")
        if self.currentEditorWidget:
            self.currentEditorWidget.scene.history.redo()

    def delete(self) -> None:
        """
        Delete selected items.
        """
        self.__logger.debug("Deleting selected items")
        if self.currentEditorWidget:
            self.currentEditorWidget.view.deleteSelected()

    def cut(self) -> None:
        """
        Cut to clipboard selected items.
        """
        self.__logger.debug("Cutting selected items")
        if self.currentEditorWidget:
            data = self.currentEditorWidget.scene.clipboard.serializeSelected(
                delete=True
            )
            strData = json.dumps(data, indent=4)
            self.clipboard.setText(strData)

    def copy(self) -> None:
        """
        Copy to clipboard selected items.
        """
        self.__logger.debug("Copying selected items")
        if self.currentEditorWidget:
            data = self.currentEditorWidget.scene.clipboard.serializeSelected(
                delete=False
            )
            strData = json.dumps(data, indent=4)
            self.__logger.debug(strData)
            self.clipboard.setText(strData)

    def paste(self):
        """
        Paste from clipboard, creating items after deserialization.
        """
        self.__logger.debug("Pasting saved items in clipboard")
        if self.currentEditorWidget:
            rawData = self.clipboard.text()
            try:
                data = json.loads(rawData)
            except ValueError as e:
                self.__logger.debug(f"Pasting of not valid json data: {e}")
                return

            # Check if json data are correct
            if "nodes" not in data:
                self.__logger.debug("JSON does not contain any blocks!")

            self.currentEditorWidget.scene.clipboard.deserialize(data)

    @staticmethod
    def getFileDialogDirectory() -> str:
        """
        Returns starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        return ""

    @staticmethod
    def getFileDialogFilter():
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "Graph (*.json);;All files (*)"

    def maybeSave(self):
        """
        If current :class:`~nodedge.scene.Scene` is modified, ask a dialog to save
        the changes.

        :return: ``True`` if the action calling this method is allowed to continue.
                 ``False`` if we should cancel operation.
        :rtype: ``bool``
        """

        if not self.currentEditorWidget.isModified:
            return True

        res = QMessageBox.warning(
            self,
            "Nodedge is about to close",
            "There are unsaved modifications. \n" "Do you want to save your changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
        )

        if res == QMessageBox.Save:
            return self.saveFile()
        elif res == QMessageBox.Cancel:
            return False

        return True

    def readSettings(self):
        """
        Read the permanent profile settings for this application.
        """
        settings = QSettings(self.companyName, self.productName)
        pos = settings.value("pos", QPoint(200, 200))
        size = settings.value("size", QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        """
        Write the permanent profile settings for this application.
        """
        settings = QSettings(self.companyName, self.productName)
        settings.setValue("pos", self.pos())
        settings.setValue("size", self.size())
