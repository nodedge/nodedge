import json

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class ViewTree(QTreeWidget):
    def __init__(self, value):

        super().__init__()

        def fill_item(item, value):
            def new_item(parent, text, val=None):
                child = QTreeWidgetItem([text])
                child.setFlags(child.flags() | Qt.ItemIsEditable)
                fill_item(child, val)
                parent.addChild(child)
                child.setExpanded(True)

            if value is None:
                return
            elif isinstance(value, dict):
                for key, val in sorted(value.items()):
                    new_item(item, str(key), val)
            elif isinstance(value, (list, tuple)):
                for val in value:
                    text = (
                        str(val)
                        if not isinstance(val, (dict, list, tuple))
                        else "[%s]" % type(val).__name__
                    )
                    new_item(item, text, val)
            else:
                new_item(item, str(value))

        fill_item(self.invisibleRootItem(), value)


if __name__ == "__main__":

    app = QApplication([])

    fname = QFileDialog.getOpenFileName()
    json_file = open(fname[0], "r")
    file = json.load(json_file)

    window = ViewTree(file)
    window.setGeometry(300, 100, 900, 600)
    window.show()
    app.exec_()
