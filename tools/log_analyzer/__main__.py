import sys

from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QApplication

from tools.log_analyzer.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    p = app.palette()
    p.setColor(QPalette.Window, QColor(53, 53, 53))
    p.setColor(QPalette.Button, QColor(53, 53, 53))
    p.setColor(QPalette.Highlight, QColor(142, 142, 142))
    p.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    p.setColor(QPalette.WindowText, QColor(255, 255, 255))
    app.setPalette(p)

    window = MainWindow()
    window.show()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
