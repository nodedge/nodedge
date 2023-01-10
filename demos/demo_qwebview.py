import sys

import markdown2
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QApplication, QMainWindow

app = QApplication(sys.argv)
mainWindow = QMainWindow()
webview = QWebEngineView()
mainWindow.setCentralWidget(webview)

# Convert the Markdown file to HTML
with open("docs/tutorials.md", "r") as md_file:
    md_content = md_file.read()
html_content = markdown2.markdown(md_content)

# Create the stylesheet
css = """
body {
    font-size: 14px;
    font-family: Arial, sans-serif;
    color: #333;
    background-color: #fff;
}
"""

# Wrap the HTML content in a `<div>` with the stylesheet applied to it
html_content = f"<div style='{css}'>{html_content}</div>"

# Load the HTML content into the webview
webview.setHtml(html_content)
webview.show()

mainWindow.show()
app.exec()
