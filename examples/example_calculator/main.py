import os
import sys
from PyQt5.QtWidgets import *

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from nodedge.mdi_window import MdiWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    window = MdiWindow()

    window.show()

    window.openFile(f"{os.path.dirname(__file__)}/example.json")

    sys.exit(app.exec_())


