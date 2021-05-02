# -*- coding: utf-8 -*-
"""
Time axis item module.
"""
import datetime

import pyqtgraph as pg


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setLabel(text="Time", units=None)
        self.enableAutoSIPrefix(False)

    def tickStrings(self, values, scale, spacing):
        return [
            datetime.datetime.fromtimestamp(value).strftime("%H:%M:%S.%f")
            if value > 0
            else ""
            for value in values
        ]
