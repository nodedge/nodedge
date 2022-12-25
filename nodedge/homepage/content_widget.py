from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.utils import loadStyleSheets

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

    def onPaletteChanged(self, text):
        self.styler.setCustomPalette(text)
        p = QApplication.palette()

        loadStyleSheets(
            # os.path.join(os.path.dirname(__file__), "qss/calculator-dark.qss"),
            self.styler.styleSheetFilename
        )

        self.paletteChanged.emit()


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
