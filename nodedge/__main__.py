# -*- coding: utf-8 -*-
import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedLayout, QWidget

from nodedge.homepage.homepage_window import HomePageWindow
from nodedge.logger import highLightLoggingSetup, setupLogging
from nodedge.mdi_window import MdiWindow
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

    window = QMainWindow()
    window.setWindowTitle("Nodedge")
    icon = QIcon(
        os.path.join(os.path.dirname(__file__), "../resources/nodedge_logo.png")
    )
    window.setWindowIcon(icon)
    widget = QWidget()
    layout = QStackedLayout()
    widget.setLayout(layout)
    mdiWindow = MdiWindow()
    # mdiWindow.openFile(
    #     f"{os.path.dirname(__file__)}/../examples/calculator/calculator.json"
    # )
    homePageWindow: HomePageWindow = HomePageWindow()

    layout.addWidget(mdiWindow)
    layout.addWidget(homePageWindow)
    window.setCentralWidget(widget)
    homePageWindow.mainWidget.headerFrame.nodedgeButton.switched.connect(
        window.centralWidget().layout().setCurrentIndex
    )
    mdiWindow.homeMenu.aboutToShow.connect(
        lambda: window.centralWidget().layout().setCurrentIndex(1)
    )
    # window = MdiWindow()
    # splash.closeSignal.connect(window.show)
    window.show()
    window.centralWidget().layout().setCurrentIndex(1)
    splash.close()

    try:
        sys.exit(app.exec())
    except Exception as e:
        dumpException(e)


if __name__ == "__main__":
    main()
