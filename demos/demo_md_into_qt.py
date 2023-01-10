import markdown2
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QLabel

app = QApplication()

with open("README.md", "r") as file:
    markdown_text = file.read()

html = markdown2.markdown(markdown_text)

label = QLabel()
label.setTextFormat(Qt.RichText)
label.setTextInteractionFlags(Qt.TextBrowserInteraction)
label.setOpenExternalLinks(True)

label.setText(html)

label.setWordWrap(True)

label.show()

app.exec_()
