import logging
import sys
from typing import Callable, Dict, Optional, Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QCompleter,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)

from nodedge.application_styler import ApplicationStyler

logger = logging.getLogger(__name__)

ELEMENT_HEIGHT = 40
MAX_ACTION_PALETTE_HEIGHT = 400


class Actionable:
    def __init__(self):
        self._actions = {}

    def createAction(
        self,
        name: str,
        callback: Callable,
        statusTip: Optional[str] = None,
        shortcut: Union[None, str, QKeySequence] = None,
        checkable: bool = False,
        category: str = "",
    ) -> QAction:
        """
        Create an action for this window and add it to actions list.

        :param name: action's name
        :type name: ``str``
        :param callback: function to be called when the action is triggered
        :type callback: ``Callable``
        :param statusTip: Description of the action displayed
            at the bottom left of the :class:`~nodedge.editor_window.EditorWindow`.
        :type statusTip: Optional[``str``]
        :param shortcut: Keyboard shortcut to trigger the action.
        :type shortcut: ``Optional[str]``
        :param checkable: if checkable, a mark will appear near the action in the menu when active.
        :type checkable: ``bool``
        :return:
        """
        act = QAction(parent=self, text=name, checkable=checkable)  # type: ignore
        act.triggered.connect(callback)

        if statusTip is not None:
            act.setStatusTip(statusTip)
            act.setToolTip(statusTip)

        if shortcut is not None:
            act.setShortcut(QKeySequence(shortcut))

        self.addAction(act)

        self._actions.update(
            {
                name: {
                    "category": category,
                    "statusTip": statusTip,
                    "shortcut": shortcut,
                }
            }
        )

        return act  # type: ignore


class ActionButton(QPushButton):
    def __init__(self, parent=None, name="", category="", shortcut=""):
        super().__init__(parent)
        self._parent = parent
        self.setMinimumHeight(ELEMENT_HEIGHT)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.label = QLabel(name)
        self.label.setMinimumWidth(100)

        self.layout.addWidget(self.label)
        self.categoryLabel = QLabel(category)
        self.layout.addWidget(self.categoryLabel)
        self.shortcutLabel = QLabel(shortcut)
        self.shortcutLabel.setAlignment(Qt.AlignRight)
        self.layout.addWidget(self.shortcutLabel)

    @property
    def name(self):
        return self.label.text()


class ActionPalette(QDialog, Actionable):
    def __init__(self, parent=None, name="", widgetNames={}):
        super().__init__()
        self._actions = {}

        self.controls = QWidget()
        self.controlsLayout = QVBoxLayout()

        self.setFixedWidth(600)

        if not widgetNames:
            widgetNames = {
                "An action": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action1": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action2": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action3": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action4": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action5": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action6": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action7": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action8": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action9": {"category": "Category A", "shortcut": "Ctrl+A"},
                "An action10": {"category": "Category B", "shortcut": "Ctrl+A"},
            }
        self.widgets: Dict[str, ActionButton] = {}

        self.fillLayout(widgetNames)

        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.controlsLayout.addItem(spacer)
        self.controls.setLayout(self.controlsLayout)

        self.scroll = QScrollArea()
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.controls)

        self.searchbar = QLineEdit()
        self.searchbar.setFixedHeight(ELEMENT_HEIGHT / 2)
        self.searchbar.textChanged.connect(self.updateDisplay)
        self.searchbar.returnPressed.connect(self.close)

        self.completer = QCompleter(widgetNames)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setCompletionMode(QCompleter.InlineCompletion)
        self.searchbar.setCompleter(self.completer)

        containerLayout = QVBoxLayout()
        containerLayout.addWidget(self.searchbar)
        containerLayout.addWidget(self.scroll)
        self.setLayout(containerLayout)

        self.selectedAction = None

        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint ^ Qt.WindowType.SplashScreen
        )

        self.searchbar.setFocus()

    def onClosedAct(self):
        self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        event.accept()

    def fillLayout(self, widgetNames):

        sortedKeys = sorted(list(widgetNames.keys()))

        for k in sortedKeys:
            v = widgetNames[k]
            if v is None:
                continue
            if k in self.widgets.keys():
                item = self.widgets[k]

            else:
                item = ActionButton(
                    name=k, category=v["category"], shortcut=v["shortcut"]
                )
                item.clicked.connect(self.onActionClicked)

            self.widgets.update({k: item})
            self.controlsLayout.addWidget(item)

    def onActionClicked(self):

        debugText = f"Action selected: {self.sender().label.text()}"
        logger.debug(debugText)
        self.selectedAction = self.sender().label.text()
        self.widgets[self.selectedAction].setChecked(True)

        self.close()

    def updateDisplay(self, text):
        count = 0

        for w in list(self.widgets.values()):
            w.hide()
        for widget in list(self.widgets.values()):
            if text.lower() in widget.name.lower():
                if count == 0:
                    widget.setDefault(True)
                    self.selectedAction = widget.label.text()
                widget.show()
                count += 1
            else:
                widget.hide()

        height = count * ELEMENT_HEIGHT + 80
        height = min(height, MAX_ACTION_PALETTE_HEIGHT)
        self.setFixedHeight(height)
        # self.resize(self.sizeHint())


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__()

        self.container = ActionPalette()
        self.setCentralWidget(self.container)

        self.setGeometry(600, 100, 800, 600)
        self.setWindowTitle("Control Panel")
        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint
            ^ Qt.WindowType.WindowStaysOnTopHint
            # ^ Qt.WindowType.
        )


if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    app = QApplication(sys.argv)
    styler = ApplicationStyler()
    w = ActionPalette()
    w.setWindowFlag(
        Qt.WindowType.FramelessWindowHint
        ^ Qt.WindowType.Tool
        # ^ Qt.WindowType.WindowStaysOnTopHint
        # ^ Qt.WindowType.SplashScreen
    )
    # w = QComboBox()
    w.show()
    sys.exit(app.exec())
