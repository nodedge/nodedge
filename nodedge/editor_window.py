# -*- coding: utf-8 -*-
"""
Editor window module containing :class:`~nodedge.editor_window.EditorWindow` class.
"""

import json
import logging
import os
from typing import Optional

from PyQt5.QtCore import QPoint, QSettings, QSize
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
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

    The editor window is the base of the multi document interface (MDI) :class:`~nodedge.mdi_window.MdiWindow`.

    The application can be opened with the :class:`~nodedge.editor_window.EditorWindow` as main window, even if
    it is not the main use case.
    """

    def __init__(self, parent: Optional[QWidget] = None):
        """
        :Instance Attributes:

        - **name_company** - name of the company, used for permanent profile settings
        - **name_product** - name of this App, used for permanent profile settings
        """

        super().__init__(parent)

        logging.basicConfig(
            format="%(asctime)s|%(levelname).4s|%(filename)10s|%(lineno).3s|"  # type: ignore
            "%(message)s|%(funcName)s".format("%Y/%m/%d %H:%M:%S")
        )

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.companyName = "Nodedge"
        self.productName = "Editor"

        QApplication.instance().clipboard().dataChanged.connect(self.onClipboardChanged)

        self.lastActiveEditorWidget = None

        self.initUI()

    @property
    def currentEditorWidget(self) -> EditorWidget:
        """
        :getter: Get current :class:`~nodedge.editor_widget.EditorWidget`

        .. note::

            The :class:`~nodedge.editor_window.EditorWindow` has only one :class:`~nodedge.editor_widget.EditorWidget`.
            This method is overridden by the :class:`~nodedge.mdi_window.MdiWindow` which may have several
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

        self.editorWidget = EditorWidget()
        self.setCentralWidget(self.editorWidget)
        self.editorWidget.scene.addHasBeenModifiedListener(self.updateTitle)

        # Initialize status bar
        self.createStatusBar()

        # Set window properties
        self.setGeometry(960, 30, 960, 960)
        self.updateTitle()
        self.show()

    # noinspection PyAttributeOutsideInit
    def createStatusBar(self) -> None:
        """
        Create Status bar and connect to :class:`~nodedge.graphics_view.GraphicsView`'s scenePosChanged event.
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
        self.newAct: QAction = QAction(
            "&New",
            self,
            shortcut="Ctrl+N",
            statusTip="Create new Nodedge",
            triggered=self.newFile,
        )

        self.openAct = QAction(
            "&Open",
            self,
            shortcut="Ctrl+O",
            statusTip="Open file",
            triggered=self.openFile,
        )
        self.saveAct = QAction(
            "&Save",
            self,
            shortcut="Ctrl+S",
            statusTip="Save file",
            triggered=self.saveFile,
        )
        self.saveAsAct = QAction(
            "Save &As",
            self,
            shortcut="Ctrl+Shift+S",
            statusTip="Save file as...",
            triggered=self.saveFileAs,
        )
        self.quitAct = QAction(
            "&Quit",
            self,
            shortcut="Ctrl+Q",
            statusTip="Exit application",
            triggered=self.close,
        )
        self.undoAct = QAction(
            "&Undo",
            self,
            shortcut="Ctrl+Z",
            statusTip="Undo last operation",
            triggered=self.undo,
        )
        self.redoAct = QAction(
            "&Redo",
            self,
            shortcut="Ctrl+Shift+Z",
            statusTip="Redo last operation",
            triggered=self.redo,
        )
        self.cutAct = QAction(
            "C&ut",
            self,
            shortcut="Ctrl+X",
            statusTip="Cut selected items",
            triggered=self.cut,
        )
        self.copyAct = QAction(
            "&Copy",
            self,
            shortcut="Ctrl+C",
            statusTip="Copy selected items",
            triggered=self.copy,
        )
        self.pasteAct = QAction(
            "&Paste",
            self,
            shortcut="Ctrl+V",
            statusTip="Paste selected items",
            triggered=self.paste,
        )
        self.deleteAct = QAction(
            "&Delete",
            self,
            shortcut="Del",
            statusTip="Delete selected items",
            triggered=self.delete,
        )

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createMenus(self) -> None:
        """
        Create Menus for `File` and `Edit`.
        """
        self.fileMenu: QMenu = self.menuBar().addMenu("&File")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAct)

        self.editMenu: QMenu = self.menuBar().addMenu("&Edit")
        self.editMenu.addAction(self.undoAct)
        self.editMenu.addAction(self.redoAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.cutAct)
        self.editMenu.addAction(self.copyAct)
        self.editMenu.addAction(self.pasteAct)
        self.editMenu.addSeparator()
        self.editMenu.addAction(self.deleteAct)

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
        clipboard = QApplication.instance().clipboard()
        self.__logger.debug(f"Clipboard changed: {clipboard.text()}")

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
                filename, filter = QFileDialog.getOpenFileName(
                    parent=self, caption="Open graph from file"
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
        Save serialized JSON version of the currently opened file, in a JSON file based on the editor's filename.
        """
        self.__logger.debug("Saving graph")
        if not self.currentEditorWidget.hasName:
            return self.saveFileAs()

        self.currentEditorWidget.saveFile(self.currentEditorWidget.filename)
        self.statusBar().showMessage(
            f"Successfully saved to {self.currentEditorWidget.shortName}", 5000
        )
        self.updateTitle()
        self.currentEditorWidget.updateTitle()
        return True

    def saveFileAs(self):
        """
        Save serialized JSON version of the currently opened file, allowing the user to choose the filename via a
        ``QFileDialog``.
        """
        self.__logger.debug("Saving graph as...")
        filename, filter = QFileDialog.getSaveFileName(
            parent=self, caption="Save graph to file"
        )

        if filename == "":
            return False

        self.currentEditorWidget.saveFile(filename)
        self.statusBar().showMessage(
            f"Successfully saved to {self.currentEditorWidget.shortName}", 5000
        )
        self.updateTitle()
        return True

    def closeEvent(self, event: QCloseEvent) -> None:
        """
        Close the window.

        Confirmation is asked to the user if there are unsaved changes.
        """
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

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
            QApplication.instance().clipboard().setText(strData)

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
            QApplication.instance().clipboard().setText(strData)

    def paste(self):
        """
        Paste from clipboard, creating items after deserialization.
        """
        self.__logger.debug("Pasting saved items in clipboard")
        if self.currentEditorWidget:
            rawData = QApplication.instance().clipboard().text()
            try:
                data = json.loads(rawData)
            except ValueError as e:
                self.__logger.debug(f"Pasting of not valid json data: {e}")
                return

            # Check if json data are correct
            if "blocks" not in data:
                self.__logger.debug("JSON does not contain any blocks!")

            self.currentEditorWidget.scene.clipboard.deserialize(data)

    def maybeSave(self):
        """
        If current :class:`~nodedge.scene.Scene` is modified, ask a dialog to save the changes.

        :return: ``True`` if the action calling this method is allowed to continue. ``False`` if we should cancel operation.
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
