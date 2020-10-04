# -*- coding: utf-8 -*-
"""
Scene Coder module containing :class:`~nodedge.scene_coder.SceneCoder` class.
"""
import logging
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
        linesOfCode: List[str] = []
        varCount = 0
        functionOutputs: List = []
        varDict: Dict[str, Any] = {}
        codingOrder: List[Node] = []

        nodes = self.scene.nodes
        edges = self.scene.edges

        num_nodes = len(nodes)
        isNodeOrdered = {nodes[i]: False for i in range(num_nodes)}

        # check if scene is codable or it is incomplete (i.e., disconnected node)
        # if codable: go ahead
        # else: exit

        # find a node that is an output
        currentNodeId = num_nodes - 1
        while currentNodeId >= 0:
            currentNode = nodes[currentNodeId]
            # if currentNode.
            if currentNode.operationCode is OP_NODE_OUTPUT:
                codingOrder.append(currentNode)
                isNodeOrdered[currentNode] = True
                break
            else:
                currentNodeId -= 1
        if not codingOrder:
            # raise error: the scene has no output
            pass

        # find parent recursively, if there is none, find one of the remaining siblings

        while True:
            parentNode = currentNode.getParentNodes()

        # serializedScene = self.scene.serialize()
        # # self.__logger.info(serializedScene)
        # serializedNodes = serializedScene["nodes"]
        # serializedEdges = serializedScene["edges"]
        # for node in serializedNodes:
        #     operationCode = node["operationCode"]
        #     nodeId = node["id"]
        #     inputSockets = node["inputSockets"]
        #     # self.__logger.info(inputSockets)
        #     if operationCode == OP_NODE_OUTPUT:
        #         inputSocketId = inputSockets[0]["id"]
        #         codingOrder.append(nodeId)
        #         previousBlockSocketId = None
        #         for edge in serializedEdges:
        #             if inputSocketId == edge["target"]:
        #                 previousBlockSocketId = edge["source"]
        #                 break
        #             elif inputSocketId == edge["source"]:
        #                 previousBlockSocketId = edge["target"]
        #                 break
        #
        #         if previousBlockSocketId is None:
        #             raise ValueError(
        #                 f"It is not possible to generate code: "
        #                 f"block #{nodeId} is not connected"
        #             )
        #
        #         previousBlockId = None
        #
        #         for otherNode in serializedNodes:
        #             otherNodeInputSocketIds = (
        #                 socket["id"] for socket in otherNode["inputSockets"]
        #             )
        #             self.__logger.info(otherNodeInputSocketIds)
        #             if previousBlockSocketId in [
        #                 *otherNode["inputSockets"],
        #                 *otherNode["outputSockets"],
        #             ]:
        #                 previousBlockId = otherNode["id"]
        #                 break
        #
        #         if previousBlockId is None:
        #             raise ValueError(
        #                 f"Socket #{previousBlockSocketId} has no " f"associated block."
        #             )
        #
        #         codingOrder.insert(0, previousBlockId)

        self.__logger.info(codingOrder)
