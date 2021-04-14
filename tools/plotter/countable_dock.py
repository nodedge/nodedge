# -*- coding: utf-8 -*-
from pyqtgraph.dockarea import Dock

from tools.plotter.utils import InstanceCounterMeta

# Metaclass for counting:
# https://stackoverflow.com/questions/8628123/counting-instances-of-a-class/47610553
# Solve metaclass conflicts:
# https://stackoverflow.com/questions/11276037/resolving-metaclass-conflicts/61350480#61350480


class CountableDockMeta(type(Dock), metaclass=InstanceCounterMeta):
    pass


class CountableDock(Dock, metaclass=CountableDockMeta):
    def __init__(self, name):
        self.id = next(self.__class__._ids)
        if name is None:
            name = f"Plot{self.id}"
        Dock.__init__(self, name=name, size=(1, 1))
        self.o = "horizontal"
        self.force = True

    def setOrientation(self, o="horizontal", force=True):
        super().setOrientation(o, force)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.setOrientation(self.o, self.force)
