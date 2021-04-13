# -*- coding: utf-8 -*-
"""
worksheet_area.py module containing :class:`~nodedge.worksheet_area.py.<ClassName>` class.
"""
from pyqtgraph.dockarea import Dock, DockArea

from tools.plotter.ranged_plot import RangedPlot


class WorksheetArea(DockArea):
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
            dock = Dock(name=dockKey)
            self.addDock(dock)

        for index, graphState in enumerate(state["graphStates"]):
            dock: Dock = self.docks[dockKeys[index]]
            rangedPlot = RangedPlot()
            rangedPlot.restoreState(graphState)
            dock.addWidget(rangedPlot)
