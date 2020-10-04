# -*- coding: utf-8 -*-
"""
Scene Coder module containing :class:`~nodedge.scene_coder.SceneCoder` class.
"""
import logging
from typing import Any, Dict, List

from nodedge.blocks import *


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
        linesOfCode: List[str] = []
        varCount = 0
        functionOutputs: List = []
        varDict: Dict[str, Any] = {}
        codingOrder: List[int] = []

        serializedScene = self.scene.serialize()
        # self.__logger.info(serializedScene)
        serializedNodes = serializedScene["nodes"]
        serializedEdges = serializedScene["edges"]
        for node in serializedNodes:
            operationCode = node["operationCode"]
            nodeId = node["id"]
            inputSockets = node["inputSockets"]
            # self.__logger.info(inputSockets)
            if operationCode == OP_NODE_OUTPUT:
                inputSocketId = inputSockets[0]["id"]
                codingOrder.append(nodeId)
                previousBlockSocketId = None
                for edge in serializedEdges:
                    if inputSocketId == edge["target"]:
                        previousBlockSocketId = edge["source"]
                        break
                    elif inputSocketId == edge["source"]:
                        previousBlockSocketId = edge["target"]
                        break

                if previousBlockSocketId is None:
                    raise ValueError(
                        f"It is not possible to generate code: "
                        f"block #{nodeId} is not connected"
                    )

                previousBlockId = None

                for otherNode in serializedNodes:
                    otherNodeInputSocketIds = (
                        socket["id"] for socket in otherNode["inputSockets"]
                    )
                    self.__logger.info(otherNodeInputSocketIds)
                    if previousBlockSocketId in [
                        *otherNode["inputSockets"],
                        *otherNode["outputSockets"],
                    ]:
                        previousBlockId = otherNode["id"]
                        break

                if previousBlockId is None:
                    raise ValueError(
                        f"Socket #{previousBlockSocketId} has no " f"associated block."
                    )

                codingOrder.insert(0, previousBlockId)

        self.__logger.info(codingOrder)


#
# for node in self.scene.nodes:
#     node.generateCode()
