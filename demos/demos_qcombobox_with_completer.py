import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QComboBox, QCompleter, QDialog, QVBoxLayout


class ComboBox(QComboBox):
    def __init__(self, parent=None):
        super(ComboBox, self).__init__(parent)
        self.setEditable(True)

        # Add some items to the combo box
        self.addItem("Item 1")
        self.addItem("Plan 2")
        self.addItem("Item difficult 3")
        self.addItem("Item 4")

        # Enable autocompletion in the combo box
        # self.setCompleter(self.completer())
        self.setEditable(True)
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.setInsertPolicy(QComboBox.NoInsert)

        # Set the combo box to be expanded when the dialog is shown
        self.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)

        self.setWindowFlag(
            Qt.WindowType.FramelessWindowHint
            ^ Qt.WindowType.WindowStaysOnTopHint
            # ^ Qt.WindowType.
        )

        self.setWindowTitle("Look for an action")
        self.setMinimumWidth(600)
        # self.combo_box.setSizePolicy(QComboBox.Expanding, QComboBox.Expanding)


class ComboBoxDialog(QDialog):
    def __init__(self):
        super().__init__()

        # Create a QComboBox and set it to be editable
        self.comboLayout = QVBoxLayout()
        self.setLayout(self.comboLayout)
        self.combo = ComboBox()

        self.comboLayout.addWidget(self.combo)

        # Set the layout of the dialog

        # Show the dialog
        # self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = ComboBoxDialog()
    combo = ComboBox()
    combo.show()
    sys.exit(app.exec())
