import sys
from PyQt5.QtWidgets import *

from nodedge.ack_editor_window import AckEditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = AckEditorWindow()

    sys.exit(app.exec_())
