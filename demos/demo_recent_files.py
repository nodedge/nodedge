import os

from PySide6.QtCore import QSettings
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QApplication, QMainWindow, QMenu


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Create a QMenu
        self.menu = QMenu("Recent Files", self)
        self.menu.aboutToShow.connect(self.updateMenu)
        self.menu.triggered.connect(self.openFile)

        # Add the QMenu to the main window
        self.menuBar().addMenu(self.menu)

        # Set up QSettings
        self.settings = QSettings("MyCompany", "MyApp")
        self.settings.beginGroup("RecentFiles")

    def updateMenu(self):
        # Clear the menu
        self.menu.clear()

        # Get the list of file paths from QSettings
        file_paths = self.settings.value("file_paths", [])

        # Add a QAction for each file path
        for file_path in file_paths:
            action = QAction(file_path, self.menu)
            action.setData(file_path)
            self.menu.addAction(action)

    def openFile(self, action):
        # Get the file path from the QAction's data
        file_path = action.data()

        # Open the file
        os.startfile(file_path)

    def addRecentFile(self, file_path):
        # Get the current list of file paths from QSettings
        file_paths = self.settings.value("file_paths", [])

        # Add the new file path to the list
        file_paths.insert(0, file_path)

        # Store the updated list in QSettings
        self.settings.setValue("file_paths", file_paths)


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec_()
