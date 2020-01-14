import inspect
import os
import sys

from PyQt5.QtWidgets import *

from nodedge.editor_window import EditorWindow
from nodedge.utils import loadStyleSheet

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa: E402


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = EditorWindow()
    window.editorWidget.addNodes()
    module_directory = os.path.dirname(inspect.getfile(window.__class__))

    loadStyleSheet(f"{module_directory}/qss/nodestyle.qss")
    sys.exit(app.exec_())
