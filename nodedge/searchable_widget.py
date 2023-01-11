import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCompleter,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler


class SimpleWidget(QWidget):
    def __init__(self, parent=None, name="", category="", shortcut=""):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel(name)
        self.label.setMinimumWidth(100)
        self.layout.addWidget(self.label)
        self.categoryLabel = QLabel(category)
        self.layout.addWidget(self.categoryLabel)
        self.shortcutLabel = QLabel(shortcut)
        self.layout.addWidget(self.shortcutLabel)
        # self.shortcut = QLineEdit()
        # self.check = QCheckBox()
        # self.check.setChecked(False)
        # self.layout.addWidget(self.check)

    @property
    def name(self):
        return self.label.text()


class SearchableWidget(QWidget):
    def __init__(self, parent=None, name=""):
        super().__init__()

        self.controls = QWidget()
        self.controlsLayout = QVBoxLayout()

        self.setFixedWidth(600)

        widget_names = {
            "An action": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action1": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action2": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action3": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action4": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action5": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action6": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action7": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action8": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action9": {"category": "A shortcut", "shortcut": "Ctrl+A"},
            "An action10": {"category": "A shortcut", "shortcut": "Ctrl+A"},
        }
        self.widgets = {}

        self.fillLayout(widget_names)

        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.controlsLayout.addItem(spacer)
        self.controls.setLayout(self.controlsLayout)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.controls)

        self.searchbar = QLineEdit()
        self.searchbar.textChanged.connect(self.update_display)

        self.completer = QCompleter(widget_names)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.InlineCompletion)
        self.searchbar.setCompleter(self.completer)

        containerLayout = QVBoxLayout()
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(self.scroll)
        self.setLayout(containerLayout)

        # self.timer = QTimer()
        # self.timer.start(1000)
        # self.timer.timeout.connect(self.updateData)

    def fillLayout(self, widget_names):

        for k, v in widget_names.items():
            if v is None:
                continue
            if k in self.widgets.keys():
                item = self.widgets[k]
                item.valueLabel.setText(v)

            else:
                item = SimpleWidget(
                    name=k, category=v["category"], shortcut=v["shortcut"]
                )

            self.widgets.update({k: item})
            self.controlsLayout.addWidget(item)

    def update_display(self, text):

        for widget in list(self.widgets.values()):
            if text.lower() in widget.name.lower():
                widget.show()
            else:
                widget.hide()
        self.updateGeometry()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.container = SearchableWidget()
        self.setCentralWidget(self.container)

        self.setGeometry(600, 100, 800, 600)
        self.setWindowTitle("Control Panel")
        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint
            ^ Qt.WindowType.WindowStaysOnTopHint
            # ^ Qt.WindowType.
        )


if __name__ == "__main__":

    app = QApplication(sys.argv)
    styler = ApplicationStyler()
    w = SearchableWidget()
    w.setWindowFlag(
        Qt.WindowType.FramelessWindowHint
        ^ Qt.WindowType.WindowStaysOnTopHint
        # ^ Qt.WindowType.SplashScreen
    )
    # w = QComboBox()
    w.show()
    sys.exit(app.exec())
