# -*- coding: utf-8 -*-
import os
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedLayout, QWidget

from nodedge.dats.dats_window import DatsWindow
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
    datsWindow: DatsWindow = DatsWindow()

    layout.addWidget(mdiWindow)
    layout.addWidget(homePageWindow)
    layout.addWidget(datsWindow)
    window.setCentralWidget(widget)
    homePageWindow.mainWidget.headerFrame.nodedgeButton.switched.connect(
        lambda: layout.setCurrentWidget(mdiWindow)
    )
    mdiWindow.homeMenu.aboutToShow.connect(
        lambda: layout.setCurrentWidget(homePageWindow)
    )

    homePageWindow.mainWidget.headerFrame.datsButton.switched.connect(
        lambda: layout.setCurrentWidget(datsWindow)
    )
    mdiWindow.homeMenu.aboutToShow.connect(
        lambda: layout.setCurrentWidget(homePageWindow)
    )

    datsWindow.homeMenu.aboutToShow.connect(
        lambda: layout.setCurrentWidget(homePageWindow)
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
