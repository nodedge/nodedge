import csv
import logging
import sys

from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QApplication, QFileDialog, QMdiArea, QTableView

from nodedge.utils import dumpException
from tools.log_analyzer.main_window import MainWindow
from tools.log_analyzer.mdi_area import MdiArea

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class LogAnalyzerWindow(MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent, applicationName="Analyzer")

        self.model = QStandardItemModel(self)

        self.tableView = QTableView(self)
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.setCentralWidget(self.tableView)

    def openFile(self, filename: str = ""):
        logger.debug(filename)
        if filename in ["", None, False]:
            filename, _ = QFileDialog.getOpenFileName(
                parent=self,
                caption="Open graph from file",
                dir=LogAnalyzerWindow.getFileDialogDirectory(),
                filter=LogAnalyzerWindow.getFileDialogFilter(),
            )

        self.loadCsv(filename)

    def loadCsv(self, fileName):
        with open(fileName, "r") as fileInput:
            for row in csv.reader(fileInput, delimiter="|", quotechar="'"):
                items = [QStandardItem(field) for field in row]
                self.model.appendRow(items)

    @staticmethod
    def getFileDialogDirectory() -> str:
        """
        Returns starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        return "../../log"

    @staticmethod
    def getFileDialogFilter() -> str:
        """
        Returns ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "Log (*.log);CSV (*.csv);All files (*)"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = LogAnalyzerWindow()
    window.showMaximized()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        dumpException(e)
