# -*- coding: utf-8 -*-
import logging
import os
import sys

from PySide6.QtCore import Qt

_logger_canmatrix = logging.getLogger("canmatrix")
_logger_canmatrix.setLevel(100)

from PySide6.QtWidgets import QApplication

from nodedge.logger import setupLogging
from nodedge.nodedge_app_window import NodedgeAppWindow
from nodedge.splash_screen import SplashScreen
from nodedge.utils import dumpException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa: E402
os.environ["QT_API"] = "pyside6"
# os.environ["QT_FONT_DPI"] = "96"  # FIX Problem for High DPI and Scale above 100%


def main():
    app: QApplication = QApplication(sys.argv)
    app.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.Floor)

    app.setApplicationName("Nodedge")
    splash = SplashScreen()
    splash.show()

    window = NodedgeAppWindow()
    setupLogging()

    # window = MdiWindow()
    # splash.closeSignal.connect(window.show)
    window.showMaximized()
    splash.close()

    try:
        sys.exit(app.exec())
    except Exception as e:
        dumpException(e)


if __name__ == "__main__":
    main()
