import os
import sys
import inspect
from PyQt5.QtWidgets import *

from nodedge.editor_window import EditorWindow
from nodedge.utils import loadStyleSheet

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditorWindow()
    module_directory = os.path.dirname(inspect.getfile(window.__class__))

    loadStyleSheet(f"{module_directory}/qss/nodestyle.qss")
    sys.exit(app.exec_())
