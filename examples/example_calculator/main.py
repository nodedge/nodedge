import sys
from PyQt5.QtWidgets import *

from nodedge.mdi_window import MdiWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MdiWindow()
    window.show()

    sys.exit(app.exec_())


