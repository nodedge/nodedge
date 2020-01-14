import os
import sys

from PyQt5.QtWidgets import *

from nodedge.mdi_window import MdiWindow

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa: E402

if __name__ == "__main__":
    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    window = MdiWindow()

    window.show()

    window.openFile(f"{os.path.dirname(__file__)}/example.json")

    sys.exit(app.exec_())
