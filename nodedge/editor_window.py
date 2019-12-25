import json
import logging
import os
import typing

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from nodedge.editor_widget import EditorWidget
from nodedge.utils import pp


class EditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        logging.basicConfig(format="%(asctime)s|%(levelname).4s|%(filename)10s|%(lineno).3s|"
                                   "%(message)s|%(funcName)s".format("%Y/%m/%d %H:%M:%S"))

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.companyName = "Nodedge"
        self.productName = "Editor"

        QApplication.instance().clipboard().dataChanged.connect(self.onClipboardChanged)

        self.lastActiveEditorWidget = None

        self.initUI()

    @property
    def currentEditorWidget(self) -> EditorWidget:
        centralWidget = self.centralWidget()
        if isinstance(centralWidget, EditorWidget):
            return typing.cast(EditorWidget, centralWidget)
        else:
            raise TypeError("Central widget is not an editor widget")

    def initUI(self):

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

    def createStatusBar(self):
        self.statusBar().showMessage("")
        self.statusMousePos = QLabel("")
        self.statusBar().addPermanentWidget(self.statusMousePos)
        self.currentEditorWidget.view.scenePosChanged.connect(self.OnScenePosChanged)

    # noinspection PyArgumentList
    def createActions(self):
        self.newAct: QAction = QAction("&New", self,
                                       shortcut="Ctrl+N", statusTip="Create new Nodedge",
                                       triggered=self.newFile)

        self.openAct = QAction("&Open", self,
                               shortcut="Ctrl+O", statusTip="Open file",
                               triggered=self.openFile)
        self.saveAct = QAction("&Save", self,
                               shortcut="Ctrl+S", statusTip="Save file",
                               triggered=self.saveFile)
        self.saveAsAct = QAction("Save &As", self,
                                 shortcut="Ctrl+Shift+S", statusTip="Save file as...",
                                 triggered=self.saveFileAs)
        self.quitAct = QAction("&Quit", self,
                               shortcut="Ctrl+Q", statusTip="Exit application",
                               triggered=self.close)
        self.undoAct = QAction("&Undo", self,
                               shortcut="Ctrl+Z", statusTip="Undo last operation",
                               triggered=self.undo)
        self.redoAct = QAction("&Redo", self,
                               shortcut="Ctrl+Shift+Z", statusTip="Redo last operation",
                               triggered=self.redo)
        self.cutAct = QAction("C&ut", self,
                              shortcut="Ctrl+X", statusTip="Cut selected items",
                              triggered=self.cut)
        self.copyAct = QAction("&Copy", self,
                               shortcut="Ctrl+C", statusTip="Copy selected items",
                               triggered=self.copy)
        self.pasteAct = QAction("&Paste", self,
                                shortcut="Ctrl+V", statusTip="Paste selected items",
                                triggered=self.paste)
        self.deleteAct = QAction("&Delete", self,
                                 shortcut="Del", statusTip="Delete selected items",
                                 triggered=self.delete)

    def createMenus(self):
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

    def updateTitle(self):
        title = "Create Nodedge"
        if self.currentEditorWidget:
            if not self.currentEditorWidget.hasName():
                title += "!"

                if self.currentEditorWidget.isModified():
                    title += "*"
            else:
                title += f" with {self.currentEditorWidget.userFriendlyFilename}"

            self.setWindowTitle(title)

            self.currentEditorWidget.updateTitle()

    def onClipboardChanged(self):
        clipboard = QApplication.instance().clipboard()
        self.__logger.debug(f"Clipboard changed: {clipboard.text()}")

    def OnScenePosChanged(self, x, y):
        self.statusMousePos.setText(f"Scene pos: {x}, {y}")

    def newFile(self):
        if self.maybeSave():
            self.__logger.info("Creating new graph")
            self.currentEditorWidget.newFile()
        self.updateTitle()

    def openFile(self):
        self.__logger.debug("Opening graph")
        if self.maybeSave():
            filename, filter = QFileDialog.getOpenFileName(parent=self, caption="Open graph from file")

            if filename == "":
                return
            if os.path.isfile(filename):
                self.currentEditorWidget.loadFile(filename)
                self.statusBar().showMessage(f"Successfully opened {os.path.basename(filename)}", 5000)

                self.updateTitle()

    def saveFile(self):
        self.__logger.debug("Saving graph")
        if not self.currentEditorWidget.hasName():
            return self.saveFileAs()

        self.currentEditorWidget.saveFile(self.currentEditorWidget.filename)
        self.statusBar().showMessage(f"Successfully saved to {self.currentEditorWidget.shortName}", 5000)
        self.updateTitle()
        self.currentEditorWidget.updateTitle()
        return True

    def saveFileAs(self):
        self.__logger.debug("Saving graph as...")
        filename, filter = QFileDialog.getSaveFileName(parent=self, caption="Save graph to file")

        if filename == "":
            return False

        self.currentEditorWidget.saveFile(filename)
        self.statusBar().showMessage(f"Successfully saved to {self.currentEditorWidget.shortName}", 5000)
        self.updateTitle()
        return True

    def closeEvent(self, event):
        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def undo(self):
        self.__logger.debug("Undoing last action")
        if self.currentEditorWidget:
            self.currentEditorWidget.scene.history.undo()

    def redo(self):
        self.__logger.debug("Redoing last action")
        if self.currentEditorWidget:
            self.currentEditorWidget.scene.history.redo()

    def delete(self):
        self.__logger.debug("Deleting selected items")
        if self.currentEditorWidget:
            self.currentEditorWidget.view.deleteSelected()

    def cut(self):
        self.__logger.debug("Cutting selected items")
        if self.currentEditorWidget:
            data = self.currentEditorWidget.scene.clipboard.serializeSelected(delete=True)
            strData = json.dumps(data, indent=4)
            QApplication.instance().clipboard().setText(strData)

    def copy(self):
        self.__logger.debug("Copying selected items")
        if self.currentEditorWidget:
            data = self.currentEditorWidget.scene.clipboard.serializeSelected(delete=False)
            strData = json.dumps(data, indent=4)
            self.__logger.debug(strData)
            QApplication.instance().clipboard().setText(strData)

    def paste(self):
        self.__logger.debug("Pasting saved items in clipboard")
        if self.currentEditorWidget:
            rawData = QApplication.instance().clipboard().text()
            try:
                data = json.loads(rawData)
            except ValueError as e:
                self.__logger.debug(f"Pasting of not valid json data: {e}")
                return

            # Check if json data are correct
            if "nodes" not in data:
                self.__logger.debug("JSON does not contain any nodes!")

            self.currentEditorWidget.scene.clipboard.deserialize(data)

    def maybeSave(self):
        if not self.currentEditorWidget.isModified():
            return True

        res = QMessageBox.warning(self, "Nodedge is about to close", "There are unsaved modifications. \n"
                                                                     "Do you want to save your changes?",
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if res == QMessageBox.Save:
            return self.saveFile()
        elif res == QMessageBox.Cancel:
            return False

        return True

    def readSettings(self):
        settings = QSettings(self.companyName, self.productName)
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings(self.companyName, self.productName)
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
