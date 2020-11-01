# -*- coding: utf-8 -*-
"""
Scene Coder module containing :class:`~nodedge.scene_coder.SceneCoder` class.
"""
import logging

from PySide2.QtCore import Signal, QObject

from nodedge.blocks import *
from nodedge.connector import Socket
from nodedge.node import Node


class SceneCoder(QObject):
    """:class:`~nodedge.scene_coder.SceneCoder` class ."""

    notConnectedSocket = Signal()

    def __init__(self, scene: "Scene", parent=None):  # type: ignore
        self.scene = scene

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)
        super().__init__(parent)

    def generateCode(self) -> str:
        """
        Generate a python function corresponding to the content of the scene.

        :return: The function as a string
        :rtype: ``str``
        """
        generatedCode: str = ""
        codingOrder: List[Node] = []
        outputNodes: List[Node] = []

        nodes = self.scene.nodes

        # check if scene is codable or it is incomplete (i.e., disconnected node)
        for node in nodes:
            outputSocket: Socket
            for outputSocket in node.outputSockets:
                if not outputSocket.hasAnyEdge:
                    self.__logger.warning(
                        f"Node {node.id} has a disconnected socket: {outputSocket.id}"
                    )
                    self.notConnectedSocket.emit()

        # if codable: go ahead
        # else: exit

        # find all output nodes
        for node in nodes:
            if node.operationCode is OP_NODE_OUTPUT:
                outputNodes.append(node)
        if not outputNodes:
            # raise error: the scene has no output
            pass

        # determine coding order
        for outputNode in outputNodes:
            # find complete hierarchy of an output node
            nodesToAdd: List[Node] = self._appendHierarchyUntilRoot(
                outputNode, codingOrder, []
            )

            # reverse order of the nodes to add and append
            if nodesToAdd:
                nodesToAdd.reverse()
                codingOrder.extend(nodesToAdd)

        # generate code
        for currentVarIndex, node in enumerate(codingOrder):
            if node not in outputNodes:
                inputNodes = node.getParentNodes()
                inputVarIndexes: List[int] = []
                for inputNode in inputNodes:
                    inputVarIndexes.append(codingOrder.index(inputNode))
                generatedCode += node.generateCode(currentVarIndex, inputVarIndexes)

        # add returned outputs
        outputVarNames: List[str] = []
        for node in outputNodes:
            inputNode = node.getParentNodes()
            inputVarIndex = codingOrder.index(inputNode[0])
            outputVarNames.append("var_" + str(inputVarIndex))
        generatedCode += "return [" + ", ".join(outputVarNames) + "]"
        self.__logger.info(codingOrder)

        return generatedCode

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
