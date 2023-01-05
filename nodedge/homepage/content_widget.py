from pathlib import Path

from PySide6.QtCore import QSettings, Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.homepage.workspace_selection_button import WorkspaceSelectionButton

MIN_HEIGHT = 30


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


class HomeContentWidget(ContentWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Welcome to Nodedge")
        self.label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.label)


class SettingsContentWidget(ContentWidget):

    paletteChanged = Signal()
    workspaceChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.layout = QFormLayout()
        # self.layout.setContentsMargins(0, 0, 0, 0)
        # self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.paletteCombo = QComboBox()
        self.paletteCombo.addItems(["Dark", "Light"])
        self.layout.addRow("Theme: ", self.paletteCombo)

        self.styler = ApplicationStyler()
        self.paletteCombo.currentTextChanged.connect(self.onPaletteChanged)

        self.workspacePath = Path("~/Nodedge")
        self.workspaceWidget = QWidget()
        self.workspaceLayout = QHBoxLayout()
        self.workspaceWidget.setLayout(self.workspaceLayout)
        self.workspaceLineEdit = QLineEdit()
        self.workspaceLineEdit.setPlaceholderText(str(self.workspacePath))
        self.workspaceLineEdit.editingFinished.connect(self.onWorkspaceChanged)
        button = WorkspaceSelectionButton(self, "...")
        self.workspaceLayout.addWidget(self.workspaceLineEdit)
        self.workspaceLayout.addWidget(button)
        self.layout.addRow("Workspace: ", self.workspaceWidget)
        button.clicked.connect(self.getPath)

    def getPath(self):
        selectedFolder = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.workspaceLineEdit.setText(selectedFolder)
        self.workspacePath = Path(selectedFolder)

    def onPaletteChanged(self, text):
        self.styler.setCustomPalette(text)
        self.paletteChanged.emit()

    def onWorkspaceChanged(self):
        text = self.workspaceLineEdit.text()
        validPath = Path.exists(Path(text))
        if validPath:
            self.workspacePath = text

        else:
            QMessageBox.warning(
                self,
                "Invalid path",
                "Invalid workspace path entered. "
                "Please, add a valid one or leave the default.",
            )
            self.workspaceLineEdit.setPlaceholderText(str(self.workspacePath))
            self.workspaceLineEdit.setText("")

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
