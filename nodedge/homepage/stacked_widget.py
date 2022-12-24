from PySide6.QtGui import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from nodedge.homepage.content_widget import ContentLabel, TitleLabel


class StackedWidget(QWidget):
    def __init__(self, parent=None, title=None, contentWidget=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # self.layout.setAlignment(Qt.AlignTop)
        self.setLayout(self.layout)

        if title is None:
            title = "Untitled"
        self.titleLabel = TitleLabel(self, title)
        self.titleLabel.setMaximumHeight(50)
        self.titleLabel.setAlignment(Qt.AlignCenter)

        if contentWidget is None:
            self.contentWidget = ContentLabel(self, "No content")
            self.contentWidget.setAlignment(Qt.AlignCenter)

        else:
            self.contentWidget = contentWidget

        self.layout.addWidget(self.titleLabel, Qt.AlignTop)
        self.layout.addWidget(self.contentWidget)
