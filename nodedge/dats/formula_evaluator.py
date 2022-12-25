import logging
import re

from asammdf import Signal
from asammdf.blocks.utils import MdfException
from asammdf.blocks.v4_blocks import Channel
from PySide6.QtWidgets import QMessageBox


def evaluateFormula(curveName, curveFormula, signals, log):
    curveFormulaNames = re.findall(r"[a-zA-Z0-9_]+", curveFormula)
    curveFormulaOperators = re.findall(r"[^a-zA-Z0-9_]+", curveFormula)

    curveFormulaNames = [i for i in curveFormulaNames if i != ""]

    for c in curveFormulaNames:
        if c.isdigit():
            curveFormulaNames.remove(c)
            continue
        if c not in signals:
            QMessageBox.warning(None, "Error", f"Signal {c} not found")
            return

    # evaluateFormula()

    # timestampsUnion = np.array([], dtype=np.float64)
    # for name in curveFormulaNames:
    #     channel: Channel = log.get(name)
    #     channel.samples = channel.samples.astype(np.float64)
    #     channel.timestamps = channel.timestamps.astype(np.float64)
    #     timestampsUnion = np.union1d(timestampsUnion, channel.timestamps)
    # timestampsUnion.sort()

    # interpolatedSamples = np.zeros(
    #     (len(timestampsUnion), len(curveFormulaNames)), dtype=np.float64
    # )
    for i, name in enumerate(curveFormulaNames):
        try:
            channel: Channel = log.get(name)
        except MdfException as e:
            logging.warning(e)
            return

        # interpolatedSamples[:, i] = np.interp(
        #     timestampsUnion, channel.timestamps, channel.samples
        # )
        if i == 0:
            channel.samples = channel.samples[0:-2]
            channel.timestamps = channel.timestamps[0:-2]
        exec(f"{name} = channel")

    try:
        newSignal: Signal = eval(curveFormula)
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Error evaluating formula: {e}")
        return

    newSignal.name = curveName

    return newSignal
