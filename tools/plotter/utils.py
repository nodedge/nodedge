# -*- coding: utf-8 -*-
# import datetime
import random
import sys
import time
import traceback
from enum import IntEnum
from functools import partial

import h5py
import numpy as np
from PySide2.QtGui import QColor
from PySide2.QtCore import QFile
from PySide2.QtWidgets import QApplication


class H5Types(IntEnum):
    GROUP = 1
    DATASET = 2


def getAllH5Keys(obj):
    "Recursively find all keys in an h5py.Group."
    keys = (obj.name,)
    types = (H5Types.GROUP,)
    if isinstance(obj, h5py.Group):
        for key, value in obj.items():
            if isinstance(value, h5py.Group):
                k, t = getAllH5Keys(value)
                keys += k
                types += t
            else:
                keys += (value.name,)
                types += (H5Types.DATASET,)

    return keys, types


def timestamp():
    # return int(time.mktime(datetime.datetime.now().timetuple()))
    return time.time()


def getDbcFileDialogDirectory() -> str:
    """
    Returns starting directory for ``QFileDialog`` DBC file open/save.

    :return: starting directory for ``QFileDialog`` DBC file open/save
    :rtype: ``str``
    """
    return "../dbc"


def getDbcFileDialogFilter() -> str:
    """
    Returns ``str`` standard file open/save filter for ``QFileDialog``

    :return: standard file open/save filter for ``QFileDialog``
    :rtype: ``str``
    """
    return "DBC (*.dbc);All files (*)"


class TracePrints(object):
    def __init__(self):
        self.stdout = sys.stdout

    def write(self, s):
        self.stdout.write("Writing %r\n" % s)
        traceback.print_stack(file=self.stdout)


def get_random_string(length):
    # put your letters in the following string
    sample_letters = "abcdefghi"
    result_str = "".join((random.choice(sample_letters) for i in range(length)))
    return result_str


def loadStyleSheets(*args):
    """
    Load multiple qss stylesheets. It concatenates them together and applies the final
    stylesheet to current QApplication instance.

    :param args: variable number of filenames of qss stylesheets
    :type args: ``str``, ``str``,...
    """
    res = ""
    for arg in args:
        file = QFile(arg)
        file.open(QFile.ReadOnly or QFile.Text)
        styleSheet = file.readAll()
        res = "\n" + str(styleSheet, encoding="utf-8")
    QApplication.instance().setStyleSheet(res)


# sys.stdout = TracePrints()
def get_color_between(color1: QColor, color2: QColor, value):
    rgb1 = np.array(color1.getRgbF())
    rgb2 = np.array(color2.getRgbF())

    rgb3 = rgb1 * value + rgb2 * (1 - value)

    color3 = QColor()
    color3.setRgbF(*rgb3.tolist())

    return color3


get_blue_scale_color = partial(get_color_between, QColor("#CAF0F8"), QColor("#03045E"))
