import logging
import os
from pathlib import Path

from PySide6.QtCore import QSettings, QSize, QStandardPaths, Qt, QUrl, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.flow_layout import FlowLayout
from nodedge.homepage.workspace_selection_button import WorkspaceSelectionButton
from nodedge.utils import cropImage, truncateString

logger = logging.getLogger(__name__)

MIN_HEIGHT = 30
BUTTON_SIZE = 200


class LinkButton(QPushButton):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.setText(text)
        # self.setMinimumHeight(40)


class FilepathButton(QPushButton):
    def __init__(self, parent, text):
        super().__init__(parent)
        self.setText(text)


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

        # urlLink = '<a href="http://www.nodedge.io">Nodedge website</a>'
        # text: str = (
        #     "For more information on Nodedge features and the latest news, please visit "
        #     + urlLink
        #     + "."
        # )
        # label = QLabel(text)
        # label.setMinimumHeight(MIN_HEIGHT)
        # self.layout.addWidget(label)
        # label.setOpenExternalLinks(True)
        #
        # urlLink = '<a href="https://nodedge.readthedocs.io/en/latest/">Nodedge API documentation</a>'
        # text: str = "For more information on the API, please visit " + urlLink + "."
        # label = QLabel(text)
        # label.setMinimumHeight(MIN_HEIGHT)
        # self.layout.addWidget(label)
        # label.setOpenExternalLinks(True)
        #
        # urlLink = (
        #     '<a href="https://github.com/nodedge/nodedge">Nodedge Github repository</a>'
        # )
        # text: str = "To checkout out the code, please visit " + urlLink + "."
        # label = QLabel(text)
        # label.setMinimumHeight(MIN_HEIGHT)
        # self.layout.addWidget(label)
        # label.setOpenExternalLinks(True)

        view = QWebEngineView(self)
        view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        view.load(QUrl("https://nodedge.io/#/tutorials"))
        self.layout.addWidget(view)
        view.show()


class FileToolButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)


class HomeContentWidget(ContentWidget):
    nodedgeFileClicked = Signal(str)
    datsFileClicked = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(50, 0, 50, 50)
        self.setLayout(self.layout)

        self.titleFrame = QFrame()
        # self.titleFrame.setFixedHeight(150)
        self.titleFrame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.titleLayout = QVBoxLayout()
        self.titleLayout.setSpacing(0)
        self.titleLayout.setContentsMargins(0, 0, 0, 50)
        self.titleLayout.setAlignment(Qt.AlignTop)
        self.titleFrame.setLayout(self.titleLayout)

        self.titleLabel = QLabel("©Nodedge")
        self.titleLabel.setAlignment(Qt.AlignLeft)
        self.titleLayout.addWidget(self.titleLabel)
        self.titleLabel.setObjectName("homeContentTitleLabel")

        self.subTitleLabel = QLabel(
            "Integrated environment for next-generation scientific programming"
        )
        self.subTitleLabel.setAlignment(Qt.AlignLeft)
        self.titleLayout.addWidget(self.subTitleLabel)
        self.subTitleLabel.setObjectName("homeContentSubTitleLabel")

        self.newsFrame = QFrame()
        # self.newsFrame.setFixedHeight(100)
        self.newsFrame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )
        self.newsLayout = QVBoxLayout()
        # self.newsLayout.setSpacing(0)
        self.newsLayout.setContentsMargins(0, 0, 0, 50)
        self.newsFrame.setLayout(self.newsLayout)

        self.newsLabel = QLabel("<b>News</b>")
        self.newsLabel.setAlignment(Qt.AlignLeft)
        self.newsLayout.addWidget(self.newsLabel)

        # TODO: add link to Nodedge download page.
        # urlLink = '<a href="https://github.com/nodedge/nodedge/releases/download/v0.4.0/NodedgeSetup.exe">Download it</a>'
        self.newsContentLabel = QLabel(
            "Nodedge has just released a new version. Download it now!"
        )
        self.newsContentLabel.setOpenExternalLinks(True)
        self.newsLayout.addWidget(self.newsContentLabel)

        self.openFrame = QFrame()
        self.openFrame.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.openLayout = QGridLayout()
        # self.openLayout.setSpacing(0)
        self.openLayout.setContentsMargins(0, 0, 0, 0)
        self.openLayout.setAlignment(Qt.AlignTop)
        self.openFrame.setLayout(self.openLayout)

        self.nodedgeOpenFrame = QFrame()
        # self.nodedgeOpenFrame.setSizePolicy(
        #     QSizePolicy.Expanding, QSizePolicy.Policy.Minimum
        # )
        # self.nodedgeOpenFrame.setFixedHeight(200)
        self.nodedgeOpenLayout = QVBoxLayout()
        # self.nodedgeOpenLayout.setSpacing(0)
        self.nodedgeOpenLayout.setContentsMargins(0, 0, 0, 50)
        self.nodedgeOpenFrame.setLayout(self.nodedgeOpenLayout)
        self.openLayout.addWidget(self.nodedgeOpenFrame, 0, 0)

        self.nodedgeOpenLabel = QLabel("<b>Start Nodedge</b>")
        self.nodedgeOpenLabel.setAlignment(Qt.AlignLeft)
        self.nodedgeOpenLayout.addWidget(self.nodedgeOpenLabel)
        self.nodedgeNewFile = LinkButton(self, "+ New file")
        self.nodedgeOpenLayout.addWidget(self.nodedgeNewFile)
        self.nodedgeOpenFile = LinkButton(self, "+ Open file")
        self.nodedgeOpenLayout.addWidget(self.nodedgeOpenFile)
        self.nodedgeOpenExample = LinkButton(self, "+ Open example")
        self.nodedgeOpenLayout.addWidget(self.nodedgeOpenExample)

        self.datsOpenFrame = QFrame()
        # self.datsOpenFrame.setFixedHeight(200)

        self.datsOpenLayout = QVBoxLayout()
        self.datsOpenLayout.setAlignment(Qt.AlignTop)
        # self.datsOpenLayout.setSpacing(0)
        self.datsOpenLayout.setContentsMargins(0, 0, 0, 50)
        self.datsOpenFrame.setLayout(self.datsOpenLayout)
        self.openLayout.addWidget(self.datsOpenFrame, 0, 1)

        self.datsOpenLabel = QLabel("<b>Start Dats</b>")
        self.datsOpenLabel.setAlignment(Qt.AlignLeft)
        self.datsOpenLayout.addWidget(self.datsOpenLabel)
        # self.datsNewFile = LinkButton(self, "New configuration")
        # self.datsOpenLayout.addWidget(self.datsNewFile)
        self.datsOpenFile = LinkButton(self, "+ Open data file")
        self.datsOpenLayout.addWidget(self.datsOpenFile)
        self.datsOpenExample = LinkButton(self, "+ Open example")
        self.datsOpenLayout.addWidget(self.datsOpenExample)

        self.createNodedgeRecentFilesWidget()
        self.createDatsRecentFilesWidget()

        self.layout.addWidget(self.titleFrame)
        self.layout.addWidget(self.newsFrame)
        self.layout.addWidget(self.openFrame)

        self.datsRecentButtons = []

    def createNodedgeRecentFilesWidget(self):
        self.recentNodedgeFrame = QFrame()
        # self.recentNodedgeFrame.setStyleSheet("background-color: green;")

        self.recentNodedgeLayout = QVBoxLayout()
        self.recentNodedgeLayout.setAlignment(Qt.AlignTop)
        self.recentNodedgeLayout.setSpacing(20)
        self.recentNodedgeLayout.setContentsMargins(0, 0, 0, 50)
        self.recentNodedgeFrame.setLayout(self.recentNodedgeLayout)
        self.openLayout.addWidget(self.recentNodedgeFrame, 1, 0)

        self.recentNodedgeLabel = QLabel("<b>Recent models</b>")
        self.recentNodedgeLayout.addWidget(self.recentNodedgeLabel)

        self.recentFilesWidget = QFrame()
        self.recentFilesLayout = FlowLayout()
        self.recentFilesLayout.setAlignment(Qt.AlignCenter)
        self.recentFilesWidget.setLayout(self.recentFilesLayout)
        self.recentNodedgeLayout.addWidget(self.recentFilesWidget)
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
                image = QPixmap(filePath)
                image = cropImage(image)
                fileButton.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
                fileButton.setIcon(image)
                fileButton.setIconSize(QSize(BUTTON_SIZE, BUTTON_SIZE))
            self.recentFilesLayout.addWidget(fileButton)
            fileButton.clicked.connect(self.onNodedgeRecentFileClicked)

    def onNodedgeRecentFileClicked(self):
        self.nodedgeFileClicked.emit(self.sender().toolTip())

    def createDatsRecentFilesWidget(self):

        self.datsRecentFilesFrame = QFrame()

        # self.recentDatsFrame.setStyleSheet("background-color: red;")
        self.datsRecentFilesLayout = QVBoxLayout()
        self.datsRecentFilesLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.datsRecentFilesLayout.setSpacing(10)
        self.datsRecentFilesLayout.setContentsMargins(0, 0, 0, 0)
        self.datsRecentFilesFrame.setLayout(self.datsRecentFilesLayout)
        self.openLayout.addWidget(self.datsRecentFilesFrame, 1, 1)

        self.datsRecentFilesLabel = QLabel("<b>Recent data files</b>")
        self.datsRecentFilesLayout.addWidget(self.datsRecentFilesLabel)

        self.datsRecentButtonsFrame = QFrame()
        self.datsRecentFilesLayout.addWidget(self.datsRecentButtonsFrame)
        self.datsRecentButtonsLayout = QVBoxLayout()
        self.datsRecentButtonsLayout.setAlignment(Qt.AlignLeft)
        self.datsRecentButtonsLayout.setContentsMargins(0, 0, 0, 0)
        self.datsRecentButtonsFrame.setLayout(self.datsRecentButtonsLayout)

    def updateDatsRecentFilesWidget(self, filePaths):

        for button in self.datsRecentButtons:
            self.datsRecentButtonsLayout.removeWidget(button)
            button.deleteLater()

        self.datsRecentButtons = []

        for index, filepath in enumerate(filePaths):
            if index > 3:
                break
            shortpath = filepath.replace("\\", "/")
            shortpath = shortpath.split("/")[-1]
            shortpath = truncateString(shortpath, 16, 8)

            fileButton = FilepathButton(self, shortpath)
            # fileButton.setFixedSize(BUTTON_SIZE, BUTTON_SIZE)
            # fileButton.setText(shortpath)
            fileButton.setToolTip(filepath)
            fileButton.clicked.connect(self.onDatsRecentFileClicked)
            self.datsRecentButtonsLayout.addWidget(fileButton)
            self.datsRecentButtons.append(fileButton)

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
        self.layout.addRow("Workspace path: ", self.workspaceWidget)
        button.clicked.connect(self.getPath)

        self.fontSizeSpinBox = QSpinBox()
        self.fontSizeSpinBox.setMinimum(10)
        self.fontSizeSpinBox.setMaximum(30)
        self.fontSizeSpinBox.setSingleStep(2)
        self.fontSizeSpinBox.setValue(14)

        self.layout.addRow("Font size: ", self.fontSizeSpinBox)
        self.fontSizeSpinBox.valueChanged.connect(self.updateFontSize)

    def updateFontSize(self, value):
        logger.debug(f"Font size changed: {value}")
        self.styler.setFontSize(str(value))

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
