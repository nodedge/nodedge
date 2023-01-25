import logging
import sys
import time
import traceback
from collections import OrderedDict
from typing import List, Optional

import numpy as np
from PySide6.QtCore import (
    QObject,
    QRunnable,
    QThread,
    QThreadPool,
    QTimer,
    Signal,
    Slot,
)
from PySide6.QtWidgets import QApplication

from nodedge.blocks import OP_NODE_CUSTOM_OUTPUT, Block
from nodedge.connector import Socket
from nodedge.node import Node
from nodedge.serializable import Serializable

logger = logging.getLogger(__name__)


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    """

    finished = Signal()
    error = Signal(tuple)
    result = Signal(object)
    progress = Signal(int)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)

        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class SolverConfiguration:
    def __init__(self):
        self.solver = None
        self.solverName = None
        self.solverOptions = None
        self.timeStep = None
        self.maxIterations = None
        self.tolerance = None
        self._finalTime = None

    @property
    def finalTime(self):
        return self._finalTime

    @finalTime.setter
    def finalTime(self, value):
        self._finalTime = float(value)

    def to_dict(self):
        return {
            "solver": self.solver,
            "solverName": self.solverName,
            "solverOptions": self.solverOptions,
            "timeStep": self.timeStep,
            "maxIterations": self.maxIterations,
            "tolerance": self.tolerance,
            "finalTime": self.finalTime,
        }

    def from_dict(self, data: dict) -> bool:
        self.solver = data["solver"]
        self.solverName = data["solverName"]
        self.solverOptions = data["solverOptions"]
        self.timeStep = data["timeStep"]
        self.maxIterations = data["maxIterations"]
        self.tolerance = data["tolerance"]
        self.finalTime = data["finalTime"]

        return True


class SceneSimulator(QObject, Serializable):
    notConnectedSocket = Signal()
    progressed = Signal(float)

    def __init__(self, scene: "Scene"):  # type: ignore
        super().__init__()
        self.config = SolverConfiguration()
        self.scene: "Scene" = scene  # type: ignore

        self.threadpool = QThreadPool()
        self.isPaused = False
        self.isStopped = False
        self.currentTimeStep = 0
        self.stepsPerSecond = 0
        self.lastCurrentStep = 0
        self.stepPerSecondTimer = QTimer()
        self.stepPerSecondTimer.timeout.connect(self._updateStepPerSecond)
        self.stepPerSecondTimer.start(1000)

    def _updateStepPerSecond(self):
        self.stepsPerSecond = self.currentTimeStep - self.lastCurrentStep
        self.lastCurrentStep = self.currentTimeStep

    def __del__(self):
        self.isStopped = True

    @property
    def totalSteps(self):
        return int(float(self.config.finalTime) / self.config.timeStep)

    @property
    def currentStep(self):
        return self.currentTimeStep / self.config.timeStep

    def generateOrderedNodeList(self) -> List[Node]:
        orderedNodeList: List[Node] = []
        outputNodes: List[Node] = []

        nodes = self.scene.nodes

        # check if scene is incomplete (i.e., disconnected node)
        # if yes, raise a warning, then go ahead
        for node in nodes:
            outputSocket: Socket
            for outputSocket in node.outputSockets:
                if not outputSocket.hasAnyEdge:
                    logger.warning(
                        f"Node {node.id} has a disconnected socket: {outputSocket.id}"
                    )
                    self.notConnectedSocket.emit()

        # if scene is not codable: raise a warning and exit

        # find all output nodes
        for node in nodes:
            if node.operationCode is OP_NODE_CUSTOM_OUTPUT:
                outputNodes.append(node)
        if not outputNodes:
            # raise error: the scene has no output
            pass

        # determine coding order
        for outputNode in outputNodes:
            # find complete hierarchy of an output node
            nodesToAdd: List[Node] = self._appendHierarchyUntilRoot(
                outputNode, orderedNodeList, []
            )

            # remove output node from the list, reverse order of the nodes to add and append
            nodesToAdd.pop(0)
            if nodesToAdd:
                nodesToAdd.reverse()
                orderedNodeList.extend(nodesToAdd)

        return orderedNodeList

    def run(self):
        self.isPaused = False
        self.isStopped = False
        self.generateOrderedNodeList()
        if self.config.finalTime is None:
            raise ValueError("Final time must be defined")

        if self.config.timeStep is None:
            raise ValueError("Time step must be defined")

        if self.config.solver is None:
            raise ValueError("Solver must be defined")

        if self.config.maxIterations is None:
            raise ValueError("Max iterations must be defined")

        if self.config.tolerance is None:
            raise ValueError("Tolerance must be defined")

        if self.config.solverName is None:
            raise ValueError("Solver name must be defined")

        try:
            finalTime = float(self.config.finalTime)
        except ValueError:
            raise ValueError("Final time must be a number")

        worker = Worker(self.runIterations, finalTime)

        app = QApplication.instance()
        app.aboutToQuit.connect(self.stop)
        # worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.scene.resetAllNodes)
        # worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)

        # self.runIterations(finalTime)

    def runIterations(self, finalTime):
        logger.info(f"Final time: {finalTime}")
        logger.info(f"Time step: {self.config.timeStep}")
        for i in np.arange(
            self.config.timeStep, finalTime + self.config.timeStep, self.config.timeStep
        ):
            logger.info(f"Running iteration {i}")
            self.currentTimeStep = i
            self.progressed.emit(i)

            while self.isPaused:
                time.sleep(0)

            if self.isStopped:
                break

            for node in self.generateOrderedNodeList():
                if not node.getParentNodes():
                    node.isDirty = True
                    node.eval()
                    node.evalChildren()

    def pause(self):
        self.isPaused = not self.isPaused

    def resume(self):
        self.isPaused = False

    def stop(self):
        self.isStopped = True

    def serialize(self):
        return OrderedDict(self.config.to_dict())

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = True,
        *args,
        **kwargs,
    ) -> bool:
        self.config = SolverConfiguration()
        deserializationValidity = self.config.from_dict(data)

        return deserializationValidity

    def updateConfig(self, config: SolverConfiguration):
        self.config = config

    def _appendHierarchyUntilRoot(
        self, currentNode: Node, appendedNodes: List[Node], nodesToAdd: List[Node]
    ):
        nodesToAdd.append(currentNode)
        parentNodes = currentNode.getParentNodes()
        if parentNodes:
            for parent in parentNodes:
                if parent not in appendedNodes and parent not in nodesToAdd:
                    self._appendHierarchyUntilRoot(parent, appendedNodes, nodesToAdd)
        return nodesToAdd
