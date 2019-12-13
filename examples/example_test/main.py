import sys
from PyQt5.QtWidgets import *

from nodedge.editor_window import EditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditorWindow()

    sys.exit(app.exec_())
