from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget

from nodedge.dats.logs_list_widget import LogsListWidget


class LogsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(1, 1, 1, 1)
        self.layout.setSpacing(1)
        self.logsListWidget = LogsListWidget()
        self.layout.addWidget(self.logsListWidget)
        self.openButton = QPushButton("Open")
        self.layout.addWidget(self.openButton)

        self.setLayout(self.layout)
