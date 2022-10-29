# -*- coding: utf-8 -*-
"""
Scene Coder module containing :class:`~nodedge.scene_coder.SceneCoder` class.
"""
import logging
from pathlib import Path
from typing import List, Tuple

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog

from nodedge.blocks import OP_NODE_CUSTOM_OUTPUT
from nodedge.connector import Socket
from nodedge.node import Node
from nodedge.utils import indentCode


class SceneCoder(QObject):
    """:class:`~nodedge.scene_coder.SceneCoder` class ."""

    notConnectedSocket = Signal()

    def __init__(self, scene: "Scene", parent=None):  # type: ignore
        super().__init__(parent)
        self.scene = scene
        self.filename: str = ""

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

    def generateCodeAndSave(self):

        orderedNodeList, generatedCode = self.generateCode()
        generatedFileString = self.addImports(orderedNodeList, generatedCode)
        self.saveFileAs(generatedFileString)
        return

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
        self.__logger.debug(orderedNodeList)

        return orderedNodeList, generatedCode

    def addImports(self, orderedNodeList, generatedCode):
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
        functionName = self._getFunctionName()
        generatedFunctionDef = f"def {functionName}():"
        generatedFunctionCall = (
            f"\n\n\nif __name__ == '__main__':\n    {functionName}()\n"
        )

        outputFileString = (
            generatedImport
            + generatedFunctionDef
            + indentCode(generatedCode)
            + generatedFunctionCall
        )

        return outputFileString

    def saveFileAs(self, outputFileString):
        """
        Choose the filename and path where to save Python generated code via a ``QFileDialog``.
        """
        self.__logger.debug("Saving generated code to file")

        # define default file name
        functionName = self._getFunctionName()
        defaultFilename = functionName + ".py"

        # open QFileDialog
        dialog: QFileDialog = QFileDialog()
        # dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)  # Set save mode: Ubuntu 18.04 shows "Open"
        self.filename, _ = dialog.getSaveFileName(
            parent=None,
            caption="Save code to file",
            dir=str(Path(SceneCoder.getFileDialogDirectory(), defaultFilename)),
            filter=SceneCoder.getFileDialogFilter(),
        )

        # if filename is empty, do nothing
        if self.filename == "":
            return

        # if filename is not empty, save to file
        self.saveFile(self.filename, outputFileString)

        return

    def saveFile(self, filename, outputFileString):
        """
        Save Python generated code to file.
        """
        with open(filename, "w") as file:
            file.write(outputFileString)
            self.__logger.debug(f"Saving to {filename} was successful.")

        return

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

    def _getFunctionName(self):
        filename = self.scene.filename
        if filename is None:
            functionName = "unnamed"
        else:
            functionName = self.scene.filename.split("/")[-1]
            functionName = functionName.split(".")[0].lower()

        return functionName

    @staticmethod
    def getFileDialogDirectory() -> str:
        """
        Return starting directory for ``QFileDialog`` file open/save

        :return: starting directory for ``QFileDialog`` file open/save
        :rtype: ``str``
        """
        return ""

    @staticmethod
    def getFileDialogFilter() -> str:
        """
        Return ``str`` standard file open/save filter for ``QFileDialog``

        :return: standard file open/save filter for ``QFileDialog``
        :rtype: ``str``
        """
        return "Python files (*.py);;All files (*)"
