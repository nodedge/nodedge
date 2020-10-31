# -*- coding: utf-8 -*-
"""
Scene Coder module containing :class:`~nodedge.scene_coder.SceneCoder` class.
"""
import logging
import string
from typing import Any, Dict, List

from nodedge.blocks import *
from nodedge.node import Node


class SceneCoder:
    """:class:`~nodedge.scene_coder.SceneCoder` class ."""

    def __init__(self, scene: "Scene"):
        self.scene = scene

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

    def generateCode(self) -> str:
        """
        Generate a python function corresponding to the content of the scene.

        :return: The function as a string
        :rtype: ``str``
        """
        # linesOfCode: List[str] = []
        # functionOutputs: List = []
        # varDict: Dict[str, Any] = {}

        generatedCode: string = ""
        codingOrder: List[Node] = []
        outputNodes: List[Node] = []

        nodes = self.scene.nodes

        # check if scene is codable or it is incomplete (i.e., disconnected node)
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
                inputVarIndexes = []
                for inputNode in inputNodes:
                    inputVarIndexes.append(codingOrder.index(inputNode))
                generatedCode += node.generateCode(currentVarIndex, inputVarIndexes)

        # add returned outputs
        outputVarNames = []
        for node in outputNodes:
            inputNode = node.getParentNodes()
            inputVarIndex = codingOrder.index(inputNode[0])
            outputVarNames.append("var_" + str(inputVarIndex))
        generatedCode += "return [" + ', '.join(outputVarNames) + "]"
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
