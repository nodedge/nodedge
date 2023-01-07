import logging
import os
from pathlib import Path

from PySide6.QtCore import QSettings, QSize, QStandardPaths, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.flow_layout import FlowLayout
from nodedge.homepage.workspace_selection_button import WorkspaceSelectionButton

logger = logging.getLogger(__name__)

MIN_HEIGHT = 30
BUTTON_SIZE = 300


class ContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class HelpContentWidget(ContentWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignCenter)
        self.setLayout(self.layout)

        urlLink = '<a href="http://www.nodedge.io">Nodedge website</a>'
        text: str = (
            "For more information on Nodedge features and the latest news, please visit "
            + urlLink
            + "."
        )
        label = QLabel(text)
        label.setMinimumHeight(MIN_HEIGHT)
        self.layout.addWidget(label)
        label.setOpenExternalLinks(True)

        urlLink = '<a href="https://nodedge.readthedocs.io/en/latest/">Nodedge API documentation</a>'
        text: str = "For more information on the API, please visit " + urlLink + "."
        label = QLabel(text)
        label.setMinimumHeight(MIN_HEIGHT)
        self.layout.addWidget(label)
        label.setOpenExternalLinks(True)

        urlLink = (
            '<a href="https://github.com/nodedge/nodedge">Nodedge Github repository</a>'
        )
        text: str = "To checkout out the code, please visit " + urlLink + "."
        label = QLabel(text)
        label.setMinimumHeight(MIN_HEIGHT)
        self.layout.addWidget(label)
        label.setOpenExternalLinks(True)


class FileToolButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)


class HomeContentWidget(ContentWidget):
    nodedgeFileClicked = Signal(str)
    datsFileClicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("<b>Open Nodedge file</b>")
        self.label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.label)

        self.createNodedgeRecentFilesWidget()
        self.datsLabel = QLabel("<b>Open Dats file</b>")
        self.datsLabel.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.datsLabel)
        self.createDatsRecentFilesWidget()

    def createNodedgeRecentFilesWidget(self):
        self.recentFilesWidget = QFrame()
        self.layout.addWidget(self.recentFilesWidget)
        self.recentFilesLayout = FlowLayout()
        self.recentFilesLayout.setAlignment(Qt.AlignCenter)
        self.recentFilesWidget.setLayout(self.recentFilesLayout)
        # self.updateNodedgeRecentFilesButtons()

    def updateNodedgeRecentFilesButtons(self, filepaths):
        self.recentFilesLayout.clear()
        for index, filepath in enumerate(filepaths):
            if index > 3:
                break
            shortpath = filepath.replace("\\", "/")
            shortpath = shortpath.split("/")[-1]
            fileButton = FileToolButton()
            fileButton.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
            fileButton.setText(shortpath)
            fileButton.setToolTip(filepath)

            dataPath = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            filename = filepath
            filename = filename.replace("\\", "_")
            filename = filename.replace("/", "_")
            filename = filename.replace(":", "_")
            filename = filename.replace(".json", "")

            filePath = os.path.join(dataPath, filename + ".png")
            if os.path.exists(filePath):
                QIcon(filePath)
                fileButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                fileButton.setIcon(QIcon(filePath))
                fileButton.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
            self.recentFilesLayout.addWidget(fileButton)
            fileButton.clicked.connect(self.onNodedgeRecentFileClicked)
        newFileButton = FileToolButton()
        newFileButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        newFileButton.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
        newFileButton.setToolTip("")
        newFileButton.setObjectName("newNodedgeFileButton")
        newFileButton.clicked.connect(self.onNodedgeRecentFileClicked)
        self.recentFilesLayout.addWidget(newFileButton)

    def onNodedgeRecentFileClicked(self):
        self.nodedgeFileClicked.emit(self.sender().toolTip())

    def createDatsRecentFilesWidget(self):
        self.datsRecentFilesWidget = QFrame()
        self.layout.addWidget(self.datsRecentFilesWidget)
        self.datsRecentFilesLayout = FlowLayout()
        self.datsRecentFilesLayout.setAlignment(Qt.AlignCenter)
        self.datsRecentFilesWidget.setLayout(self.datsRecentFilesLayout)

    def updateDatsRecentFilesWidget(self, filePaths):
        self.datsRecentFilesLayout.clear()
        for index, filepath in enumerate(filePaths):
            if index > 4:
                break
            shortpath = filepath.replace("\\", "/")
            shortpath = shortpath.split("/")[-1]
            fileButton = FileToolButton()
            fileButton.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
            fileButton.setText(shortpath)
            fileButton.setToolTip(filepath)

            dataPath = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            filename = filepath
            filename = filename.replace("\\", "_")
            filename = filename.replace("/", "_")
            filename = filename.replace(":", "_")
            filename = filename.replace(".json", "")

            filePath = os.path.join(dataPath, filename + ".png")
            if os.path.exists(filePath):
                QIcon(filePath)
                fileButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                fileButton.setIcon(QIcon(filePath))
                fileButton.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
            self.datsRecentFilesLayout.addWidget(fileButton)
            fileButton.clicked.connect(self.onDatsRecentFileClicked)

    def onDatsRecentFileClicked(self):
        self.datsFileClicked.emit(self.sender().toolTip())


class SettingsContentWidget(ContentWidget):

    paletteChanged = Signal()
    workspaceChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QFormLayout()
        self.layout.setAlignment(Qt.AlignCenter)

        # self.layout.setContentsMargins(0, 0, 0, 0)
        # self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.paletteCombo = QComboBox()
        self.paletteCombo.addItems(["Dark", "Light"])
        self.layout.addRow("Theme: ", self.paletteCombo)

        self.styler = ApplicationStyler()
        self.paletteCombo.currentTextChanged.connect(self.onPaletteChanged)

        self.defaultWorkspacePath = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation
        )
        self.restoreDefaultPath()
        self.workspacePath = Path(self.defaultWorkspacePath)
        self.workspaceWidget = QWidget()
        self.workspaceLayout = QHBoxLayout()
        self.workspaceWidget.setLayout(self.workspaceLayout)
        self.workspaceLayout.setSpacing(10)
        self.workspaceLayout.setContentsMargins(0, 0, 0, 0)
        self.workspaceLineEdit = QLineEdit()
        self.workspaceLineEdit.setText(str(self.workspacePath))
        self.workspaceLineEdit.returnPressed.connect(self.workspaceLineEdit.clearFocus)
        self.workspaceLineEdit.editingFinished.connect(self.onWorkspaceChanged)
        button = WorkspaceSelectionButton(self, "...")
        button.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.workspaceLayout.addWidget(self.workspaceLineEdit)
        self.workspaceLayout.addWidget(button)
        self.layout.addRow("Workspace: ", self.workspaceWidget)
        button.clicked.connect(self.getPath)

    def getPath(self):
        selectedFolder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not selectedFolder:
            return
        self.workspaceLineEdit.setText(selectedFolder)
        self.workspacePath = selectedFolder

        self.onWorkspaceChanged()

    def restoreDefaultPath(self):
        settings = QSettings("Nodedge", "Nodedge")

        defaultWorkspacePath = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation
        )
        self.defaultWorkspacePath = settings.value(
            "workspacePath", defaultWorkspacePath
        )

    def onPaletteChanged(self, text):
        self.styler.setCustomPalette(text)
        self.paletteChanged.emit()

    def onWorkspaceChanged(self):
        text = self.workspaceLineEdit.text()
        validPath = Path.exists(Path(text))
        if validPath and text != "":
            self.workspacePath = text
            logger.debug(f"Workspace path updated: {self.workspacePath}")

            settings = QSettings("Nodedge", "Nodedge")
            settings.setValue("workspacePath", self.workspacePath)

        else:
            QMessageBox.warning(
                self,
                "Invalid path",
                "Invalid workspace path entered. "
                "Please, add a valid one or leave the default.",
            )
            self.workspaceLineEdit.setText(str(self.workspacePath))
            # self.workspaceLineEdit.setText("")

        self.workspaceChanged.emit(self.workspacePath)


class TitleLabel(QLabel):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)
        self.setText(text)
        self.setMaximumHeight(50)
        self.setAlignment(Qt.AlignCenter)


class ContentLabel(QLabel):
    def __init__(self, parent=None, text=None):
        super().__init__(parent)
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
