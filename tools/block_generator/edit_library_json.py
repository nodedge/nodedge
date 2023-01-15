import pandas as pd
from PySide6.QtWidgets import (
    QApplication,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

configFile = r"tools/block_generator/numpy_block_config.json"


class BlockConfigTableWidget(QWidget):
    def __init__(self):
        super(BlockConfigTableWidget, self).__init__()

        # Read JSON file into a Pandas dataframe
        df = pd.read_json(configFile)

        # Create a Qself.tableWidget
        self.table = QTableWidget()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)

        # Add data to the self.table
        for i in range(len(df)):
            for j in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iloc[i, j]))
                self.table.setItem(i, j, item)

        # Create a save button
        save_button = QPushButton("Save")

        # Connect the save button to a slot function
        save_button.clicked.connect(self.save_table)

        # Create a vertical layout to hold the self.table and the save button
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(save_button)

        # Create a QWidget to hold the layout
        self.setLayout(layout)

    def save_table(self):
        """Slot function to save the self.table to a JSON file"""
        # Create a Pandas dataframe from the self.table data
        data = []
        for i in range(self.table.rowCount()):
            row_data = []
            for j in range(self.table.columnCount()):
                item = self.table.item(i, j)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append(None)
            data.append(row_data)
        df = pd.DataFrame(
            data,
            columns=[
                self.table.horizontalHeaderItem(i).text()
                for i in range(self.table.columnCount())
            ],
        )

        # Save the dataframe to a JSON file
        df.to_json(configFile, orient="records", indent=4)


if __name__ == "__main__":
    app = QApplication()

    widget = BlockConfigTableWidget()

    # Show the widget
    widget.show()

    app.exec()
