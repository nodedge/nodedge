import sys
from PySide6 import QtCore
from PySide6.QtCore import Signal
from PySide6.QtGui import (QColor)
from PySide6.QtWidgets import *

from graphics_splash_screen import GraphicsSplashScreen

# Define a global counter
counter = 0


class SplashScreen(QMainWindow):
    closeSignal = Signal()

    def __init__(self):
        QMainWindow.__init__(self, None)
        self.ui = GraphicsSplashScreen()
        self.ui.setupUi(self)

        # Remove title bar
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Drop shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.ui.dropShadowFrame.setGraphicsEffect(self.shadow)

        # Start QTimer (counting in milliseconds)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(35)

        # Initial text
        self.ui.labelDescription.setText("<strong>Welcome</strong> to Nodedge")

        # You can change text indicating what is loading
        # QtCore.QTimer.singleShot(1000, lambda: self.ui.labelDescription.setText("<strong>Loading</strong> Nodedge core"))
        # QtCore.QTimer.singleShot(1000, lambda: self.ui.labelDescription.setText("<strong>Loading</strong> user interface"))

        # Show Main Window
        self.show()

    def progress(self):

        global counter
        self.ui.progressBar.setValue(counter)

        if counter > 100:
            self.timer.stop()

            # Show Nodedge MainWindow
            # Close splash screen
            self.closeSignal.emit()
            self.close()

        # Increase counter
        counter += 10


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SplashScreen()
    main = QMainWindow(None)
    window.closeSignal.connect(main.show)

    sys.exit(app.exec_())
