# -*- coding: utf-8 -*-
"""
worksheet_area.py module containing :class:`~nodedge.worksheet_area.py.<ClassName>` class.
"""
from pyqtgraph.dockarea import Dock, DockArea
from PySide2.QtCore import Signal
from PySide2.QtWidgets import QWidget

from tools.plotter.countable_dock import CountableDock
from tools.plotter.ranged_plot import RangedPlot


class WorksheetArea(DockArea):
    restoreCurves = Signal(object)

    def __init__(self):
        super().__init__()

    def saveState(self):
        state = super().saveState()
        keys = list(self.docks.data.keys())
        graphStates = []
        for key in keys:
            dock = self.docks[key]
            graph: RangedPlot = dock.widgets[0].graph
            graphStates.append(graph.saveState())
        state["graphStates"] = graphStates

        return state

    def restoreState(self, state, missing="ignore", extra="bottom"):
        super().restoreState(state, missing, extra)
        dockKeys = []
        for dockState in state["main"][1]:
            dockKey = dockState[1]
            dockKeys.append(dockKey)
            dock = CountableDock(name=dockKey)
            self.addDock(dock)

        for index, graphState in enumerate(state["graphStates"]):
            dock: Dock = self.docks[dockKeys[index]]
            rangedPlot = RangedPlot()
            rangedPlot.restoreCurves.connect(self.restoreCurves)
            rangedPlot.restoreState(graphState)
            dock.addWidget(rangedPlot)
            dock.setTitle(rangedPlot.curveNames[0])

    def mouseReleaseEvent(self, ev):
        QWidget.mouseReleaseEvent(self, ev)
        print("Mew")
