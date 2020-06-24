import os
import sys

from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

from nodedge.mdi_window import MdiWindow
from nodedge.utils import dumpException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa: E402


if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")
    p = app.palette()
    p.setColor(QPalette.Window, QColor(53, 53, 53))
    p.setColor(QPalette.Button, QColor(53, 53, 53))
    p.setColor(QPalette.Highlight, QColor(142, 45, 197))
    p.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    p.setColor(QPalette.WindowText, QColor(255, 255, 255))
    app.setPalette(p)

    window = MdiWindow()

    window.show()

    window.openFile(f"{os.path.dirname(__file__)}/example.json")

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
