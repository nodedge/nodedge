# -*- coding: utf-8 -*-
import os
import sys

from PySide6.QtWidgets import QApplication

from nodedge.logger import highLightLoggingSetup, setupLogging
from nodedge.mdi_window import MdiWindow
from nodedge.utils import dumpException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa: E402
os.environ["QT_API"] = "pyside6"


def main():
    app: QApplication = QApplication(sys.argv)
    setupLogging()
    highLightLoggingSetup()

    window = MdiWindow()
    window.show()
    window.openFile(
        f"{os.path.dirname(__file__)}/../examples/calculator/calculator.json"
    )
    try:
        sys.exit(app.exec())
    except Exception as e:
        dumpException(e)


if __name__ == "__main__":
    main()
