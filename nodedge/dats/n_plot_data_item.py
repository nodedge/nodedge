from pyqtgraph import PlotDataItem
from PySide6.QtGui import QMouseEvent


class NPlotDataItem(PlotDataItem):
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)

    def mouseClickEvent(self, ev: QMouseEvent):
        super().mouseClickEvent(ev)

    def setData(self, *args, **kargs):
        super().setData(*args, **kargs)
