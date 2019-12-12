import json
import logging
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from nodedge.ack_editor_widget import AckEditorWidget


class AckEditorWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        logging.basicConfig(format="%(asctime)s|%(levelname).4s|%(filename)10s|%(lineno).3s|"
                                   "%(message)s|%(funcName)s".format("%Y/%m/%d %H:%M:%S"))

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)


        self.companyName = "Nodedge"
        self.filename = None

        QApplication.instance().clipboard().dataChanged.connect(self.onClipboardChanged)

        self.initUI()

    def initUI(self):
        menuBar: QMenuBar = self.menuBar()

        # Initialize menus
        fileMenu: QMenu = menuBar.addMenu("&File")
        self.addActionToMenu(fileMenu, "&New", "Ctrl+N", "Create new Nodedge", self.onNewFile)
        fileMenu.addSeparator()
        self.addActionToMenu(fileMenu, "&Open", "Ctrl+O", "Open file", self.onOpenFile)
        self.addActionToMenu(fileMenu, "&Save", "Ctrl+S", "Save file", self.onSaveFile)
        self.addActionToMenu(fileMenu, "Save &As", "Ctrl+Shift+S", "Save file as...", self.onSaveFileAs)
        fileMenu.addSeparator()
        self.addActionToMenu(fileMenu, "&Quit", "Ctrl+Q", "Exit application", self.close)

        editMenu = menuBar.addMenu("&Edit")
        self.addActionToMenu(editMenu, "&Undo", "Ctrl+Z", "Undo last operation", self.onUndo)
        self.addActionToMenu(editMenu, "&Redo", "Ctrl+Shift+Z", "Redo last operation", self.onRedo)
        editMenu.addSeparator()
        self.addActionToMenu(editMenu, "C&ut", "Ctrl+X", "Cut selected items", self.onCut)
        self.addActionToMenu(editMenu, "&C&opy", "Ctrl+C", "Copy selected items", self.onCopy)
        self.addActionToMenu(editMenu, "&C&opy", "Ctrl+V", "Paste selected items", self.onPaste)
        editMenu.addSeparator()
        self.addActionToMenu(editMenu, "&Delete", "Del", "Delete selected items", self.onDelete)

        layoutMenu = menuBar.addMenu("&Layout")
        helpMenu = menuBar.addMenu("&Help")

        nodeEditor = AckEditorWidget()
        nodeEditor.scene.addHasBeenModifiedListener(self.updateTitle)
        self.setCentralWidget(nodeEditor)

        # Initialize status bar
        self.statusBar().showMessage("")
        self.statusMousePos = QLabel("")
        self.statusBar().addPermanentWidget(self.statusMousePos)
        self.centralWidget().view.scenePosChanged.connect(self.OnScenePosChanged)

        # Set window properties
        self.setGeometry(960, 30, 960, 960)
        self.updateTitle()
        self.show()

    def createActions(self):
        pass

    def updateTitle(self):
        title = "Create nodedge"
        if self.filename is None:
            title += "!"
        else:
            title += f"with {os.path.basename(self.filename)}"

        if self.centralWidget().scene.hasBeenModified:
            title += "*"

        self.setWindowTitle(title)

    def addActionToMenu(self, menu, name, shortcut, tooltip, callback):
        act = QAction(name, self)
        act.setShortcut(shortcut)
        act.setToolTip(tooltip)
        act.triggered.connect(callback)
        menu.addAction(act)

    def onClipboardChanged(self):
        clipboard = QApplication.instance().clipboard()
        self.__logger.debug(f"Clipboard changed: {clipboard.text()}")

    def OnScenePosChanged(self, x, y):
        self.statusMousePos.setText(f"Scene pos: {x}, {y}")

    def onNewFile(self):
        if self.maybeSave():
            self.centralWidget().scene.clear()
            self.__logger.info("Creating new graph")
            self.filename = None
        self.updateTitle()

    def onOpenFile(self):
        if self.maybeSave():
            filename, filter = QFileDialog.getOpenFileName(parent=self, caption="Open graph from file")

            if filename == "":
                return
            if os.path.isfile(filename):
                self.centralWidget().scene.loadFromFile(filename)
                self.filename = filename

            self.updateTitle()

            self.__logger.debug("Opening graph")

    def onSaveFile(self):
        if self.filename is None:
            return self.onSaveFileAs()

        self.centralWidget().scene.saveToFile(self.filename)
        self.__logger.debug("Saving graph")
        self.statusBar().showMessage(f"Successfully saved to {self.filename}")

        self.updateTitle()

        return True

    def onSaveFileAs(self):
        filename, filter = QFileDialog.getSaveFileName(parent=self, caption="Save graph to file")

        if filename == "":
            return False

        self.filename = filename
        self.onSaveFile()

        self.__logger.debug("Saving graph as...")
        return True

    def onUndo(self):
        self.centralWidget().scene.history.undo()
        self.__logger.debug("Undoing last action")

    def onRedo(self):
        self.centralWidget().scene.history.redo()
        self.__logger.debug("Redoing last action")

    def onDelete(self):
        self.centralWidget().view.deleteSelected()
        self.__logger.debug("Deleting selected items")

    def onCut(self):
        self.__logger.debug("Cutting selected items")
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=True)
        strData = json.dumps(data, indent=4)
        QApplication.instance().clipboard().setText(strData)

    def onCopy(self):
        self.__logger.debug("Copying selected items")
        data = self.centralWidget().scene.clipboard.serializeSelected(delete=False)
        strData = json.dumps(data, indent=4)
        self.__logger.debug(strData)
        QApplication.instance().clipboard().setText(strData)

    def onPaste(self):
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

        self.centralWidget().scene.clipboard.deserialize(data)

    def closeEvent(self, event):

        if self.maybeSave():
            event.accept()
        else:
            event.ignore()

    def maybeSave(self):
        if not self.isModified():
            return True

        res = QMessageBox.warning(self, "Nodedge is about to close", "There are unsaved modifications. \n"
                                                                          "Do you want to save your changes?",
                                  QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

        if res == QMessageBox.Save:
            return self.onSaveFile()
        elif res == QMessageBox.Cancel:
            return False

        return True

    def isModified(self):
        return self.centralWidget().scene.hasBeenModified

    def readSettings(self):
        settings = QSettings('Trolltech', 'MDI Example')
        pos = settings.value('pos', QPoint(200, 200))
        size = settings.value('size', QSize(400, 400))
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QSettings('Trolltech', 'MDI Example')
        settings.setValue('pos', self.pos())
        settings.setValue('size', self.size())
