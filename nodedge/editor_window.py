import json
import logging
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from nodedge.editor_widget import EditorWidget


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

        self.initUI()

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
        self.currentEditorWidget().view.scenePosChanged.connect(self.OnScenePosChanged)

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
        self.delAct = QAction("&Delete", self,
                              shortcut="Del", statusTip="Delete selected items",
                              triggered=self.delete)

    def createMenus(self):
        fileMenu: QMenu = self.menuBar().addMenu("&File")
        fileMenu.addAction(self.newAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.openAct)
        fileMenu.addAction(self.saveAct)
        fileMenu.addAction(self.saveAsAct)
        fileMenu.addSeparator()
        fileMenu.addAction(self.quitAct)

        editMenu: QMenu = self.menuBar().addMenu("&Edit")
        editMenu.addAction(self.undoAct)
        editMenu.addAction(self.redoAct)
        editMenu.addSeparator()
        editMenu.addAction(self.cutAct)
        editMenu.addAction(self.copyAct)
        editMenu.addAction(self.pasteAct)
        editMenu.addSeparator()
        editMenu.addAction(self.delAct)

    def updateTitle(self):
        title = "Create Nodedge"
        if not self.currentEditorWidget().hasName():
            title += "!"

            if self.currentEditorWidget().isModified():
                title += "*"
        else:
            title += f" with {self.currentEditorWidget().userFriendlyFilename()}"

        self.setWindowTitle(title)

    def currentEditorWidget(self):
        return self.centralWidget()

    def onClipboardChanged(self):
        clipboard = QApplication.instance().clipboard()
        self.__logger.debug(f"Clipboard changed: {clipboard.text()}")

    def OnScenePosChanged(self, x, y):
        self.statusMousePos.setText(f"Scene pos: {x}, {y}")

    def newFile(self):
        if self.maybeSave():
            self.currentEditorWidget().scene.clear()
            self.__logger.info("Creating new graph")
            self.filename = None
        self.updateTitle()

    def openFile(self):
        if self.maybeSave():
            filename, filter = QFileDialog.getOpenFileName(parent=self, caption="Open graph from file")

            if filename == "":
                return
            if os.path.isfile(filename):
                self.currentEditorWidget().scene.loadFromFile(filename)
                self.currentEditorWidget().filename = filename

            self.updateTitle()

            self.__logger.debug("Opening graph")

    def saveFile(self):
        if self.filename is None:
            return self.saveFileAs()

        self.currentEditorWidget().scene.saveToFile(self.filename)
        self.__logger.debug("Saving graph")
        self.statusBar().showMessage(f"Successfully saved to {self.filename}")

        self.updateTitle()

        return True

    def saveFileAs(self):
        filename, filter = QFileDialog.getSaveFileName(parent=self, caption="Save graph to file")

        if filename == "":
            return False

        self.filename = filename
        self.saveFile()

        self.__logger.debug("Saving graph as...")
        return True

    def undo(self):
        self.currentEditorWidget().scene.history.undo()
        self.__logger.debug("Undoing last action")

    def redo(self):
        self.currentEditorWidget().scene.history.redo()
        self.__logger.debug("Redoing last action")

    def delete(self):
        self.currentEditorWidget().view.deleteSelected()
        self.__logger.debug("Deleting selected items")

    def cut(self):
        self.__logger.debug("Cutting selected items")
        data = self.currentEditorWidget().scene.clipboard.serializeSelected(delete=True)
        strData = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(strData)

    def copy(self):
        self.__logger.debug("Copying selected items")
        data = self.currentEditorWidget().scene.clipboard.serializeSelected(delete=False)
        strData = json.dumps(data, indent=4)
        self.__logger.debug(strData)
        QApplication.instance().clipboard().setText(strData)

    def paste(self):
        self.__logger.debug("Pasting saved items in clipboard")
        rawData = QApplication.instance().clipboard().text()

        try:
            data = json.loads(rawData)
        except ValueError as e:
            self.__logger.debug(f"Pasting of not valid json data: {e}")
            return

        # Check if json data are correct
        if "nodes" not in data:
            self.__logger.debug("JSON does not contain any nodes!")

        self.currentEditorWidget().scene.clipboard.deserialize(data)

    def maybeSave(self):
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "Nodedge is about to close", "There are unsaved modifications. \n"
                                                                     "Do you want to save your changes?",
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if res == QMessageBox.Save:
            return self.saveFile()
        elif res == QMessageBox.Cancel:
            return False

        return True

    def isModified(self):
        return self.currentEditorWidget().scene.isModified

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
