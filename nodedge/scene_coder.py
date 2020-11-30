# -*- coding: utf-8 -*-
"""
Scene Coder module containing :class:`~nodedge.scene_coder.SceneCoder` class.
"""
import logging
from typing import List, Tuple

from PySide2.QtCore import QObject, Signal

from nodedge.blocks.block_config import OP_NODE_OUTPUT
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

    def generateCode(self) -> Tuple[List[Node], str]:
        """
        Generate a python function corresponding to the content of the scene.

        :return: The function as a string
        :rtype: ``str``
        """
        generatedCode: str = ""
        orderedNodeList: List[Node] = []
        outputNodes: List[Node] = []

        nodes = self.scene.nodes

        # check if scene is incomplete (i.e., disconnected node)
        # if yes, raise a warning, then go ahead
        for node in nodes:
            outputSocket: Socket
            for outputSocket in node.outputSockets:
                if not outputSocket.hasAnyEdge:
                    self.__logger.warning(
                        f"Node {node.id} has a disconnected socket: {outputSocket.id}"
                    )
                    self.notConnectedSocket.emit()  # type: ignore

        # if scene is not codable: raise a warning and exit

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
                outputNode, orderedNodeList, []
            )

            # remove output node from the list, reverse order of the nodes to add and append
            nodesToAdd.pop(0)
            if nodesToAdd:
                nodesToAdd.reverse()
                orderedNodeList.extend(nodesToAdd)

        # generate code for all nodes
        for currentVarIndex, node in enumerate(orderedNodeList):
            inputNodes = node.getParentNodes()
            inputVarIndexes: List[int] = []
            for inputNode in inputNodes:
                inputVarIndexes.append(orderedNodeList.index(inputNode))
            generatedCode += node.generateCode(currentVarIndex, inputVarIndexes)

        # add returned output list
        outputVarNames: List[str] = []
        for node in outputNodes:
            inputNode = node.getParentNodes()
            inputVarIndex = orderedNodeList.index(inputNode[0])
            outputVarNames.append("var_" + str(inputVarIndex))
        generatedCode += "return [" + ", ".join(outputVarNames) + "]"
        self.__logger.info(orderedNodeList)

        return orderedNodeList, generatedCode

    def createFileFromGeneratedCode(self, orderedNodeList, generatedCode):
        # add imports on top
        importedLibraries = {}
        for currentVarIndex, node in enumerate(orderedNodeList):
            if node.evalString and node.library:
                if node.library not in importedLibraries:
                    importedLibraries[node.library] = []
                importedLibraries[node.library].append(node.evalString)
        generatedImport = ""

        for key in importedLibraries.keys():
            generatedImport += (
                f"from {key} import {', '.join(importedLibraries[key])}\n"
            )
        generatedImport += "\n\n"

        # put code into a function
        functionName = self.scene.filename.split("/")[-1]
        functionName = functionName.split(".")[0].lower()
        generatedFunctionDef = f"def {functionName}():"
        generatedFunctionCall = (
            f"\n\n\nif __name__ == '__main__':\n    {functionName}()\n"
        )

        outputFileString = (
            generatedImport
            + generatedFunctionDef
            + _indent_code(generatedCode)
            + generatedFunctionCall
        )

        return outputFileString

    def createFile(self) -> str:
        orderedNodeList, generatedCode = self.generateCode()
        fileString = self.createFileFromGeneratedCode(orderedNodeList, generatedCode)
        return fileString

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


def _indent_code(string: str):
    lines = string.split("\n")
    indentedLines = ["\n    " + line for line in lines]
    indentedCode = "".join(indentedLines)
    return indentedCode
