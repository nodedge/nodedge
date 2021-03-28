# -*- coding: utf-8 -*-
import pyqtgraph as pg
from pyqtgraph.examples.syntax import QColor

from tools.plotter.utils import get_blue_scale_color


class BarGraphItem(pg.BarGraphItem):
    def __init__(
        self,
        x,
        height,
        brushes=None,
        width=1,
        brushes_depend_on_height=False,
    ):
        self.brushes_depend_on_height = brushes_depend_on_height
        self.x = x
        self.height = height
        self.width = width
        self.brushes = brushes
        self.barInitialized = [False for _ in range(len(x))]

        super().__init__(
            x=x,
            height=height,
            width=width,
            brushes=brushes,
        )

    def setAttr(self, **opts):
        if "x" in opts:
            self.x = opts["x"]
        if "height" in opts:
            self.height = opts["height"]
        if "width" in opts:
            self.width = opts["width"]
        if self.brushes_depend_on_height:
            self.updateBrushesDependingOnHeight()
            opts.update({"brushes": self.brushes})
        else:
            if "brushes" in opts:
                self.brushes = opts["brushes"]
        super().setOpts(**opts)

    def updateBrushesDependingOnHeight(self):
        brushes = [
            get_blue_scale_color(float(self.height[i]) / 2.5)
            for i in range(len(self.x))
        ]
        for i, b in enumerate(self.brushes):
            if self.barInitialized[i]:
                if self.height[i] < 0 or self.height[i] > 2.5:
                    self.brushes[i] = QColor("red")
                else:
                    self.brushes[i] = brushes[i]
