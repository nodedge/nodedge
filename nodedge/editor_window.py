# -*- coding: utf-8 -*-
"""
Editor window module containing :class:`~nodedge.editor_window.EditorWindow` class.
"""
import json
import logging
import os
from typing import Callable, Optional, Union, cast

from PySide6.QtCore import QSettings, QSize, Qt
from PySide6.QtGui import (
    QAction,
    QClipboard,
    QCloseEvent,
    QGuiApplication,
    QKeySequence,
)
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.editor_widget import EditorWidget
from nodedge.scene_coder import SceneCoder


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

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.companyName = "Nodedge"
        self.productName = "Editor"

        self.instance: QGuiApplication = cast(
            QGuiApplication, QGuiApplication.instance()
        )

        self.styler = ApplicationStyler()

        self.clipboard: QClipboard = self.instance.clipboard()

        # Pycharm does not recognise resolve connect method so the inspection is
        # noinspection PyUnresolvedReferences
        self.clipboard.dataChanged.connect(self.onClipboardChanged)  # type: ignore

        self.lastActiveEditorWidget: Optional[EditorWidget] = None

        self.debugMode: bool = False

        self.initUI()

    @property
    def currentEditorWidget(self) -> Optional[EditorWidget]:
        """
        :getter: Get current :class:`~nodedge.editor_widget.EditorWidget`

        .. note::

            The :class:`~nodedge.editor_window.EditorWindow` has only one
            :class:`~nodedge.editor_widget.EditorWidget`. This method is overridden
            by the :class:`~nodedge.mdi_window.MdiWindow` which may have several
            :class:`~nodedge.editor_widget.EditorWidget`.

        :rtype: Optional[:class:`~nodedge.editor_widget`]
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

        self.editorWidget = self.__class__.EditorWidgetClass()
        self.setCentralWidget(self.editorWidget)
        self.editorWidget.scene.addHasBeenModifiedListener(self.updateTitle)

        self.createActions()

        self.createMenus()

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

        if self.currentEditorWidget is None:
            return

        self.currentEditorWidget.graphicsView.scenePosChanged.connect(
            self.OnScenePosChanged
        )

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

        self.fitInViewAct = self.createAction(
            "Fit in view",
            self.onFitInView,
            "Fit content in view",
            QKeySequence(Qt.Key_Space),
        )

        self.generateCodeAct = self.createAction(
            "Generate code",
            self.onGenerateCode,
            "Generate python code",
            QKeySequence("Ctrl+G"),
        )

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createMenus(self) -> None:
        """
        Create Menus for `File` and `Edit`.
        """
        self.createFileMenu()
        self.createEditMenu()
        self.createViewMenu()
        self.createCoderMenu()

    # noinspection PyArgumentList, PyAttributeOutsideInit, DuplicatedCode
    def createCoderMenu(self):
        self.coderMenu: QMenu = self.menuBar().addMenu("&Coder")
        self.coderMenu.addAction(self.generateCodeAct)

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

    # noinspection PyAttributeOutsideInit
    def createViewMenu(self) -> None:
        """
        Create view menu.
        """
        self.viewMenu: QMenu = self.menuBar().addMenu("&View")
        self.viewMenu.addAction(self.fitInViewAct)

    def sizeHint(self) -> QSize:
        """
        Qt size hint handle.
        TODO: Investigate if we really need to overwrite this method.

        :return: ``None``
        """
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
        """
        Slot called when the clipboard has changed.

        :return: ``None``
        """
        self.__logger.debug(f"Clipboard changed: '{self.clipboard.text()}'")

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
                    dir=EditorWindow.getFileDialogDirectory(),
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
            dir=EditorWindow.getFileDialogDirectory(),
            filter=EditorWindow.getFileDialogFilter(),
        )

        if filename == "":
            return

        self.beforeSaveFileAs(self.currentEditorWidget, filename)
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

    def quit(self) -> None:
        """
        Callback when the user decides to close the application.

        :return: ``None``
        """
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
            self.currentEditorWidget.graphicsView.deleteSelected()

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
            data = self.currentEditorWidget.scene.clipboard.serializeSelected()
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
    def getFileDialogFilter() -> str:
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

        if self.currentEditorWidget is None or not self.currentEditorWidget.isModified:
            return True

        res = QMessageBox.warning(
            self,
            "Nodedge is about to close",
            "There are unsaved modifications. \n" "Do you want to save your changes?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

        if res == QMessageBox.StandardButton.Save:
            return self.saveFile()
        elif res == QMessageBox.StandardButton.Cancel:
            return False

        return True

    def readSettings(self):
        """
        Read the permanent profile settings for this application.
        """
        settings = QSettings(self.companyName, self.productName)
        self.restoreGeometry(settings.value("geometry"))
        self.restoreState(settings.value("windowState"))
        self.debugMode = settings.value("debug", False)

    def writeSettings(self):
        """
        Write the permanent profile settings for this application.
        """
        settings = QSettings(self.companyName, self.productName)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        settings.setValue("debug", self.debugMode)

    def beforeSaveFileAs(
        self, currentEditorWidget: EditorWidget, filename: str
    ) -> None:
        """
        Event triggered after choosing filename and before actual fileSave(). Current
        :class:`~nodedge.editor_widget.EditorWidget` is passed because focus is lost
        after asking with ``QFileDialog`` and therefore `getCurrentNodeEditorWidget`
        will return ``None``.

        :param currentEditorWidget: :class:`~nodedge.editor_widget.EditorWidget`
            currently focused
        :type currentEditorWidget: :class:`~nodedge.editor_widget.EditorWidget`
        :param filename: name of the file to be saved
        :type filename: ``str``
        """
        pass

    def onFitInView(self):
        if self.currentEditorWidget is not None:
            self.currentEditorWidget.graphicsView.graphicsScene.fitInView()

    def onGenerateCode(self):
        if self.currentEditorWidget is not None:
            coder: SceneCoder = self.currentEditorWidget.scene.coder
            if coder is not None:
                self.currentEditorWidget.scene.coder.generateCodeAndSave()
                successStr = f"File saved to {coder.filename}"
                self.__logger.debug(successStr)
                self.statusBar().showMessage(successStr, 5000)

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
