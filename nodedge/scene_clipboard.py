# -*- coding: utf-8 -*-
"""
Scene clipboard module containing :class:`~nodedge.scene_clipboard.SceneClipboard`.
"""

import logging
from collections import OrderedDict

from nodedge.edge import Edge
from nodedge.graphics_edge import GraphicsEdge


class SceneClipboard:
    """
    :class:`~nodedge.scene_clipboard.SceneClipboard` class

    The scene clipboard class contains the code for the serialization/deserialization
    from/to the clipboard.
    """

    def __init__(self, scene: "Scene") -> None:  # type: ignore
        self.scene = scene

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

    def serializeSelected(self, delete=False):
        """
        Serializes selected items in the scene into ``OrderedDict``.

        :param delete: ``True`` to delete selected items after serialization.
            It is useful for cut operations.
        :type delete: ``bool``
        :return: serialized data of current selection in Nodedge's :class:`~nodedge.scene.Scene`
        """
        self.__logger.debug("Copying to clipboard")

        serializedSelectedNodes, selectedEdges, selectedSocket = [], [], {}

        # Sort edges and blocks
        for item in self.scene.graphicsScene.selectedItems():
            if hasattr(item, "node"):
                serializedSelectedNodes.append(item.node.serialize())
                for socket in item.node.inputSockets + item.node.outputSockets:
                    selectedSocket[socket.id] = socket
            elif isinstance(item, GraphicsEdge):
                selectedEdges.append(item.edge)

        self.__logger.debug(f"Nodes: {serializedSelectedNodes}")
        self.__logger.debug(f"Edges: {selectedEdges}")
        self.__logger.debug(f"Sockets: {selectedSocket}")

        # Remove all edges which are not connected to a node in our list
        edgesToRemove = []
        for edge in selectedEdges:
            if (
                edge.sourceSocket.id not in selectedSocket
                or edge.destinationSocket.id not in selectedSocket
            ):
                self.__logger.debug(f"Edge: {edge} is not connected with both sides")
                edgesToRemove.append(edge)

        for edge in edgesToRemove:
            selectedEdges.remove(edge)

        serializedEdgesToKeep = [edge.serialize() for edge in selectedEdges]
        # Create data
        data = OrderedDict(
            [("blocks", serializedSelectedNodes), ("edges", serializedEdgesToKeep)]
        )

        # If cut (aka delete) remove selected items
        if delete:
            self.scene.view.deleteSelected()
            # Store history
            self.scene.history.store("Cut out selected items from scene")

        return data

    def deserialize(self, data):
        """
        Deserializes data from the clipboard.

        :param data: ``dict`` data for deserialization to the :class:`Nodedge.node_scene.Scene`
        :type data: ``dict``
        """
        hashmap = {}

        # Calculate mouse scene position
        view = self.scene.view
        mouseScenePos = view.lastSceneMousePos

        # Calculate selected objects bounding box and center
        minX, maxX, minY, maxY = 1e8, -1e8, 1e8, -1e8
        for nodeData in data["blocks"]:
            x, y = nodeData["posX"], nodeData["posY"]
            if x < minX:
                minX = x
            if x > maxX:
                maxX = x
            if y < minY:
                minY = y
            if y > maxY:
                maxY = y
        boundedBoxCenterX = (minX + maxX) / 2
        boundedBoxCenterY = (minY + maxY) / 2

        # center = view.mapToScene(view.rect().center)

        # Calculate the offset of newly created blocks
        offsetX = mouseScenePos.x() - boundedBoxCenterX
        offsetY = mouseScenePos.y() - boundedBoxCenterY

        # Create each node

        for nodeData in data["blocks"]:
            newNode = self.scene.getNodeClassFromData(nodeData)(self.scene)
            newNode.deserialize(nodeData, hashmap, restoreId=False)

            # Reajust the new node position
            pos = newNode.pos
            newNode.pos = (pos.x() + offsetX, pos.y() + offsetY)

        # Create each edge
        if "edges" in data:
            for edgeData in data["edges"]:
                newEdge = Edge(self.scene)
                newEdge.deserialize(edgeData, hashmap, restoreId=False)

        # Store history
        self.scene.history.store("Paste items in scene.")

        self.__logger.debug(f"Deserializing from clipboard: {data}")
