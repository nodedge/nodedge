import logging
from collections import OrderedDict
from typing import List, Optional

import numpy as np
from PySide6.QtCore import Signal

from nodedge.blocks import OP_NODE_CUSTOM_OUTPUT
from nodedge.connector import Socket
from nodedge.node import Node
from nodedge.serializable import Serializable

logger = logging.getLogger(__name__)


class SolverConfiguration:
    def __init__(self):
        self.solver = None
        self.solverName = None
        self.solverOptions = None
        self.timeStep = None
        self.maxIterations = None
        self.tolerance = None
        self.finalTime = None

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


class SceneSimulator(Serializable):
    notConnectedSocket = Signal()
    simulatorStep = Signal(int)

    def __init__(self, scene: "Scene"):  # type: ignore
        super().__init__()
        self.config = SolverConfiguration()
        self.scene: "Scene" = scene  # type: ignore

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

        self.runIterations(finalTime)

    def runIterations(self, finalTime):
        for i in np.arange(0, finalTime, self.config.timeStep):

            for node in self.generateOrderedNodeList():
                if not node.getParentNodes():
                    node.isDirty = True
                    node.eval()
                    node.evalChildren()

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
