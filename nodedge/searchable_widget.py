import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
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


class SimpleWidget(QWidget):
    def __init__(self, parent=None, name="", value=""):
        super().__init__()

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel(name)
        self.label.setMinimumWidth(100)
        self.layout.addWidget(self.label)
        self.valueLabel = QLabel(value)
        self.layout.addWidget(self.valueLabel)
        self.check = QCheckBox()
        self.check.setChecked(False)
        self.layout.addWidget(self.check)

    @property
    def name(self):
        return self.label.text()


class SearchableWidget(QWidget):
    def __init__(self, parent=None, name=""):
        super().__init__()

        self.controls = QWidget()
        self.controlsLayout = QVBoxLayout()

        widget_names = {
            "An action": "A shortcut",
            "An action1": "A shortcut",
            "An action2": "A shortcut",
            "An action3": "A shortcut",
            "An action4": "A shortcut",
            "An action5": "A shortcut",
            "An action6": "A shortcut",
            "An action7": "A shortcut",
            "An action8": "A shortcut",
            "An action9": "A shortcut",
            "An action10": "A shortcut",
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
                item = SimpleWidget(name=k, value=v)

            self.widgets.update({k: item})
            self.controlsLayout.addWidget(item)

    def update_display(self, text):

        for widget in list(self.widgets.values()):
            if text.lower() in widget.name.lower() or widget.check.isChecked():
                widget.show()
            else:
                widget.hide()


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
    w = SearchableWidget()
    # w = QComboBox()
    w.show()
    sys.exit(app.exec())
