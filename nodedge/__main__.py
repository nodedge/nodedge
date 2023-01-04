# -*- coding: utf-8 -*-
import os
import sys

from PySide6.QtWidgets import QApplication

from nodedge.logger import highLightLoggingSetup, setupLogging
from nodedge.nodedge_app_window import NodedgeAppWindow
from nodedge.splash_screen import SplashScreen
from nodedge.utils import dumpException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa: E402
os.environ["QT_API"] = "pyside6"


def main():
    app: QApplication = QApplication(sys.argv)
    splash = SplashScreen()
    splash.show()
    setupLogging()
    highLightLoggingSetup()

    window = NodedgeAppWindow()

    # window = MdiWindow()
    # splash.closeSignal.connect(window.show)
    window.show()
    splash.close()

    try:
        sys.exit(app.exec())
    except Exception as e:
        dumpException(e)


if __name__ == "__main__":
    main()
