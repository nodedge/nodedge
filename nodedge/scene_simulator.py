import logging
import sys
import time
import traceback
from collections import OrderedDict
from typing import List, Optional, Tuple

import control as ct
import numpy as np
from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Signal, Slot
from PySide6.QtWidgets import QApplication

from nodedge.blocks import (
    OP_NODE_CUSTOM_OUTPUT,
    Block,
    ConstantBlock,
    NumpyAddBlock,
    NumpySubtractBlock,
    OutputBlock,
)
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
            "solverOptions": self.solverOptions,
            "timeStep": self.timeStep,
            "maxIterations": self.maxIterations,
            "tolerance": self.tolerance,
            "finalTime": self.finalTime,
        }

    def from_dict(self, data: dict) -> bool:
        self.solver = data["solver"]
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
        if self.config.solver is None:
            raise ValueError("Solver must be defined")
        elif self.config.solver == "Basic solver":
            self.runBasicSolver()
        elif self.config.solver == "Python control solver":
            self.runPythonControlSolver()

    def runBasicSolver(self):
        self.isPaused = False
        self.isStopped = False
        self.generateOrderedNodeList()
        if self.config.finalTime is None:
            raise ValueError("Final time must be defined")

        if self.config.timeStep is None:
            raise ValueError("Time step must be defined")

        if self.config.maxIterations is None:
            raise ValueError("Max iterations must be defined")

        if self.config.tolerance is None:
            raise ValueError("Tolerance must be defined")

        try:
            finalTime = float(self.config.finalTime)
        except ValueError:
            raise ValueError("Final time must be a number")

        worker = Worker(self._runIterationsBasicSolver, finalTime)

        app = QApplication.instance()
        app.aboutToQuit.connect(self.stop)
        # worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.scene.resetAllNodes)
        # worker.signals.progress.connect(self.progress_fn)

        # Execute
        self.threadpool.start(worker)

    def runPythonControlSolver(self):
        systems: List[ct.NonlinearIOSystem] = []
        sumSubBlocks: List[ct.LinearIOSystem] = []
        inputBlocks: List[str] = []
        outputBlocks: List[str] = []
        connections: List[Tuple[str, str]] = []
        for n in self.scene.nodes:
            if not isinstance(n, Block):
                logger.warning(f"Node {n.title} is not a block")
                continue

            if isinstance(n, NumpyAddBlock):
                inputNode1 = n.inputNodesAt(0)[0].title

                inputNode2 = n.inputNodesAt(1)[0].title
                outputNode = n.outputNodesAt(0)[0].title
                subBlock: ct.LinearIOSystem = ct.summing_junction(
                    inputs=[
                        f"{inputNode1}.y[0]",
                        f"{inputNode2}.y[0]",
                    ],
                    output=f"{outputNode}.u[0]",
                    name=f"{n.title}_sum",
                )
                sumSubBlocks.append(subBlock)
                logger.debug(f"Add block: {subBlock}")
            elif isinstance(n, NumpySubtractBlock):
                name = f"{n.title}_sub"
                inputNode1 = n.inputNodesAt(0)[0]
                if isinstance(inputNode1, ConstantBlock):
                    inputNode1 = f"{inputNode1.title}_y"
                else:
                    inputNode1 = f"{inputNode1.title}_y[0]"
                inputNode2 = n.inputNodesAt(1)[0]
                if isinstance(inputNode2, ConstantBlock):
                    inputNode2 = f"{inputNode2.title}_y"
                else:
                    connections.append(
                        (f"{name}.{inputNode2.title}_y[0]", f"{inputNode2.title}.y[0]")
                    )

                    inputNode2 = f"{inputNode2.title}_y[0]"
                outputNode = n.outputNodesAt(0)[0]
                connections.append(
                    (f"{outputNode.title}.u[0]", f"{name}.{outputNode.title}_u[0]")
                )
                subBlock: ct.LinearIOSystem = ct.summing_junction(
                    inputs=[
                        inputNode1,
                        "-" + inputNode2,  # Notice the minus sign
                    ],
                    output=f"{outputNode.title}_u[0]",
                    name=name,
                )
                # sumBlock.output_labels = [f"{outputNode}.u[0]"]
                sumSubBlocks.append(subBlock)

                logger.debug(f"Subtract block: {subBlock}")

            elif isinstance(n, ConstantBlock):
                inputBlock = f"{n.title}_y"
                inputBlocks.append(inputBlock)
                logger.debug(f"Constant block: {inputBlock}")
            elif isinstance(n, OutputBlock):
                outputBlock = f"{n.inputNodeAt(0).title}.y[0]"
                outputBlocks.append(outputBlock)
                logger.debug(f"Output block: {outputBlock}")
            else:
                sys = n.ioSystem
                logger.debug(f"Created new system: {sys}")

                systems.append(n.ioSystem)

                inputNode = n.inputNodeAt(0)
                if isinstance(inputNode, NumpyAddBlock) or isinstance(
                    inputNode, NumpySubtractBlock
                ):
                    continue
                # while isinstance(inputNode, NumpyAddBlock) or isinstance(
                #     inputNode, NumpySubtractBlock
                # ):
                #     inputNode = inputNode.inputNodeAt(0)

                outputNode = n
                connection = (
                    f"{outputNode.title}.u[0]",
                    f"{inputNode.title}.y[0]",
                )
                logger.debug(f"Created new connection: {connection}")
                connections.append(connection)

        logger.debug(f"Sum/Sub blocks: {sumSubBlocks}")
        logger.debug(f"Input blocks: {inputBlocks}")
        logger.debug(f"Output blocks: {outputBlocks}")
        logger.debug(f"Connections: {connections}")
        logger.debug(f"Systems: {systems}")

        io_closed = ct.interconnect(
            [s for s in sumSubBlocks + systems],
            connections=connections,
            inplist=inputBlocks,
            outlist=outputBlocks,
        )

        logger.debug(f"IO closed: {io_closed}")

        time = np.linspace(0, 10, 100)
        t, y = ct.input_output_response(io_closed, time, 30, [0])

        logger.debug(f"Time: {t}")
        logger.debug(f"Y: {y}")

    def _runIterationsBasicSolver(self, finalTime):
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
