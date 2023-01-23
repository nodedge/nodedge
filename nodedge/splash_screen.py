import sys

from PySide6 import QtCore
from PySide6.QtCore import QRect, Signal
from PySide6.QtGui import QColor, QFont, Qt
from PySide6.QtWidgets import *

counter = 0
SPLASH_WIDTH = 680
SPLASH_HEIGHT = 400


class SplashScreen(QMainWindow):
    closed = Signal()

    def __init__(self):
        QMainWindow.__init__(self, None)

        self.setWindowTitle("Nodedge loading")

        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint
            ^ Qt.WindowType.WindowStaysOnTopHint
            ^ Qt.WindowType.SplashScreen
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(SPLASH_WIDTH, SPLASH_HEIGHT)
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.dropShadowFrame = QFrame(self.centralWidget)
        self.dropShadowFrame.setFrameShape(QFrame.Shape.StyledPanel)
        self.dropShadowFrame.setFrameShadow(QFrame.Shadow.Raised)
        self.dropShadowFrame.setStyleSheet(
            "QFrame {	\n"
            "	background-color: #1B1D23;	\n"
            "	color: #23252E;\n"
            "	border-radius: 10px;\n"
            "}"
        )

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.verticalLayout.addWidget(self.dropShadowFrame)

        self.labelTitle = QLabel(self.dropShadowFrame)
        self.labelTitle.setGeometry(QRect(0, 90, 661, 61))
        self.labelTitle.setFont(QFont(["Segoe UI"], 36, QFont.Weight.Bold))
        self.labelTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelTitle.setText("NODEDGE")
        self.labelTitle.setStyleSheet("color: #2860AC;")

        self.labelDescription = QLabel(self.dropShadowFrame)
        self.labelDescription.setGeometry(QRect(0, 150, 661, 61))
        self.labelDescription.setFont(QFont(["Segoe UI"], 14))
        self.labelDescription.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelDescription.setText("Welcome to Nodedge")
        self.labelDescription.setStyleSheet("color: #4B5063;")

        self.progressBar = QProgressBar(self.dropShadowFrame)
        self.progressBar.setGeometry(QRect(50, 280, 561, 23))
        self.progressBar.setValue(0)
        self.progressBar.setStyleSheet(
            "QProgressBar {\n"
            "	\n"
            "	background-color: #23252E;\n"
            "	color: #C8C8C8;\n"
            "	border-style: none;\n"
            "	border-radius: 10px;\n"
            "	text-align: center;\n"
            "}\n"
            "QProgressBar::chunk{\n"
            "	border-radius: 10px;\n"
            "	background-color: qlineargradient("
            "spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523, "
            "stop:0 rgba(251, 255, 0, 255), "
            "stop:1 rgba(255, 150, 0, 255));\n"
            "}"
        )

        self.labelLoading = QLabel(self.dropShadowFrame)
        self.labelLoading.setGeometry(QRect(0, 320, 661, 21))
        self.labelLoading.setFont(QFont(["Segoe UI"], 12))
        self.labelLoading.setStyleSheet("color: #4B5063;")
        self.labelLoading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelLoading.setText("Loading ...")

        self.labelCredits = QLabel(self.dropShadowFrame)
        self.labelCredits.setGeometry(QRect(20, 350, 621, 21))
        self.labelCredits.setFont(QFont(["Segoe UI"], 10))
        self.labelCredits.setStyleSheet("color: #4B5063;")
        self.labelCredits.setAlignment(
            Qt.AlignmentFlag.AlignRight
            | Qt.AlignmentFlag.AlignTrailing
            | Qt.AlignmentFlag.AlignVCenter
        )
        self.labelCredits.setText("Copyright (c) 2020-2022 Nodedge Foundation")

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(35)

        # QtCore.QTimer.singleShot(1000, lambda: self.labelDescription.setText("<strong>Loading</strong> Nodedge core"))

        self.show()

    def updateProgress(self):

        global counter
        self.progressBar.setValue(counter)

        if counter > 100:
            self.timer.stop()

            self.closed.emit()
            self.close()

        counter += 1


if __name__ == "__main__":
    app = QApplication()

    window = SplashScreen()
    main = QMainWindow(None)
    window.closed.connect(main.show)

    sys.exit(app.exec())
