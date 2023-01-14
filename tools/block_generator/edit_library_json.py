import pandas as pd
from PySide6.QtWidgets import QApplication, QTableWidget, QTableWidgetItem

configFile = r"tools/block_generator/numpy_block_config.json"


app = QApplication()

# Read JSON file into a Pandas dataframe
df = pd.read_json(configFile)

# Create a QTableWidget
table = QTableWidget()
table.setRowCount(len(df))
table.setColumnCount(len(df.columns))

# Add data to the table
for i in range(len(df)):
    for j in range(len(df.columns)):
        item = QTableWidgetItem(str(df.iloc[i, j]))
        table.setItem(i, j, item)

# Show the table
table.show()

app.exec_()
