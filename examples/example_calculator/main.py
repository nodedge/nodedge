import sys
from PyQt5.QtWidgets import *

from nodedge.mdi_window import MdiWindow
from nodedge.utils import loadStyleSheet

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    window = MdiWindow()
    window.show()

    sys.exit(app.exec_())


