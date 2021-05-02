# -*- coding: utf-8 -*-
"""
write_read_h5_file.py module containing :class:`~nodedge.write_read_h5_file.py.<ClassName>` class.
"""

import sys
import time
from datetime import datetime

import numpy as np
import pyqtgraph as pg
from h5py import *
from pyqtgraph import DateAxisItem
from PySide2.QtWidgets import QApplication

from tools.plotter.time_axis_item import TimeAxisItem
from tools.plotter.utils import timestamp

with File("mytestfile.hdf5", "w") as f:
    t = []
    d = []
    arr = np.array([])
    # dset = f.create_dataset("mydataset", (10, 1), dtype="i")
    for i in range(100):
        d.append(np.random.randint(0, 100, 1)[0])
        time.sleep(1e-6)
        t.append(timestamp())
    data = np.array(d)
    time = np.array(t)
    f["time"] = time.astype(opaque_dtype(time.dtype))
    f["data"] = data
    print(f["data"])


with File("mytestfile.hdf5", "r") as f:
    read_dset = f["data"]
    # print(read_dset)
    # print(f["time"][0])

    t = f["time"][:]
    d = f["data"][:]

    app = QApplication([])

    axis = TimeAxisItem(orientation="bottom")
    w = pg.PlotWidget(axisItems={"bottom": axis})

    # Add the Date-time axis
    # w.addItem(axis)
    # axis.attachToPlotItem(w.getPlotItem())

    # plot some random data with timestamps in the last hour
    # now = time.time()
    # timestamps = np.linspace(now - 3600, now, 100)
    w.plot(x=t, y=d, symbol="o")

    w.show()

    sys.exit(app.exec_())
