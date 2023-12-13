# -*- coding: utf-8 -*-
"""
${FILE_NAME} module containing :class:`~nodedge.${FILE_NAME}.<ClassName>` class.
"""
import logging
import os

import numpy as np
import pyqtgraph as pg
import pyqtgraph.exporters

from nodedge.utils import butterLowpassFilter

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def test_butter_lowpass_filter():
    inArr = np.ones(100)
    noise = np.random.normal(0, 0.1, 100)
    inArr += noise
    logger.debug(inArr)

    outArr = butterLowpassFilter(inArr, 0.1, 1, 1)
    logger.debug(outArr)

    plt = pg.plot(inArr, pen=pg.mkPen("b", width=1), name="original")
    plt.plot(outArr, pen=pg.mkPen("r", width=1), name="filtered")
    exporter = pg.exporters.ImageExporter(plt.plotItem)
    exporter.parameters()["width"] = 1500
    outputPath = "tests_outputs/utils_tests"
    outputFilename = outputPath + "/test_butter_lowpass_filter.png"
    if os.path.exists(outputFilename):
        os.remove(outputFilename)
    else:
        os.makedirs(outputPath, exist_ok=True)
    exporter.export(outputFilename)

    assert np.greater_equal(outArr, np.min(inArr)).all()
    assert np.less_equal(outArr, np.max(inArr)).all()
    assert np.std(outArr) < np.std(inArr)
