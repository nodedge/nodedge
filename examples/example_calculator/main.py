import os
import sys

from PySide2.QtGui import QColor, QPalette
from PySide2.QtWidgets import QApplication

from nodedge.mdi_window import MdiWindow
from nodedge.utils import dumpException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa: E402
os.environ["QT_API"] = "pyside"

if __name__ == "__main__":
    app: QApplication = QApplication(sys.argv)

    QApplication.setStyle("Fusion")
    p = QApplication.palette()
    raisinBlackDark = QColor("#1B1D23")
    raisinBlackLight = QColor("#272C36")
    raisinBlackMid = QColor("#23252E")
    charCoal = QColor("#363A46")
    independence = QColor("#464B5B")
    white = QColor("#DDFFFFFF")
    blue = QColor("#007BFF")
    spanishGray = QColor("#999999")
    dimGray = QColor("#666666")

    p.setColor(QPalette.AlternateBase, blue)
    p.setColor(QPalette.Base, charCoal)
    p.setColor(QPalette.BrightText, blue)
    p.setColor(QPalette.Button, raisinBlackDark)
    p.setColor(QPalette.ButtonText, white)
    p.setColor(QPalette.Dark, raisinBlackDark)
    p.setColor(QPalette.Highlight, blue)
    p.setColor(QPalette.HighlightedText, white)
    p.setColor(QPalette.Light, independence)
    p.setColor(QPalette.Link, spanishGray)
    p.setColor(QPalette.LinkVisited, dimGray)
    p.setColor(QPalette.Mid, raisinBlackMid)
    p.setColor(QPalette.Midlight, raisinBlackLight)
    p.setColor(QPalette.Shadow, independence)
    p.setColor(QPalette.Text, white)
    p.setColor(QPalette.Window, charCoal)
    p.setColor(QPalette.WindowText, white)
    app.setPalette(p)

    window = MdiWindow()

    window.show()

    window.openFile(f"{os.path.dirname(__file__)}/example.json")

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
