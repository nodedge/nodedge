import os
import sys

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QImage, QPixmap
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QApplication, QPushButton


class AnimatedSvgExample(QSvgWidget):
    def __init__(self):
        super().__init__()
        self.__initUi()

    def __initUi(self):
        r = self.renderer()
        r.setFramesPerSecond(60)
        ico_filename = os.path.join(os.path.dirname(__file__), "ico/rolling.svg")
        r.load(ico_filename)


class SvgButton(QPushButton):
    def __init__(self):
        super().__init__()

        self.setFlat(True)
        self.setCheckable(True)
        self.setIconSize(QSize(160, 160))
        self.setText("A MEOW BUTTON")
        self.filename = "resources/lucide/activity.svg"

        # svgRenderer = QSvgRenderer("resources/lucide/activity.svg")
        # pix = QPixmap(svgRenderer.defaultSize())
        #
        xmlContent = (
            "<svg version='1.1' viewBox='0 0 32 32'"
            " xmlns='http://www.w3.org/2000/svg'>"
            "<circle cx='16' cy='16' r='4.54237' fill='#FF0000'/></svg>"
        )

        # mycolor = QInputDialog.getColor()
        style = """
        QPushButton
        {
            color: red;
        }
        """

        xmlContent = (
            f'<svg version="1.1" viewBox="0 0 32 32"'
            f' xmlns="http://www.w3.org/2000/svg">'
            f'<circle cx="16" cy="16" r="32" fill="#00FF00"/></svg>'
        ).encode("utf-8")

        # xmlContent = (
        #     b'<svg version="1.1" viewBox="0 0 32 32"'
        #     b' xmlns="http://www.w3.org/2000/svg">'
        #     b'<circle cx="16" cy="16" r="4.54237"/></svg>'
        # )

        icon = QIcon(QPixmap.fromImage(QImage.fromData(xmlContent)))

        # icon = QIcon("resources/lucide/activity.svg")
        self.setIcon(icon)
        self.setStyleSheet(style)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    r = SvgButton()
    r.show()
    sys.exit(app.exec())
