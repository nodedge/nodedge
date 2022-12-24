from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QLabel,
    QSizePolicy,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler
from nodedge.utils import loadStyleSheets


class ContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)


class HelpContentWidget(ContentWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QFormLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.layout.addRow(QLabel("Help"))


class HomeContentWidget(ContentWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QFormLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)

        self.label = QLabel("Welcome to Nodedge")
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
