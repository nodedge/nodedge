import json
import logging
import os
from collections import OrderedDict
from typing import Callable, List

from PyQt5.QtGui import QDragEnterEvent, QDropEvent

from nodedge.edge import Edge
from nodedge.graphics_scene import GraphicsScene
from nodedge.node import Node
from nodedge.scene_clipboard import SceneClipboard
from nodedge.scene_history import SceneHistory
from nodedge.serializable import Serializable
from nodedge.utils import dumpException


class Scene(Serializable):
    def __init__(self):
        super().__init__()
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.sceneWidth = 64000
        self.sceneHeight = 64000

        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        self._isModified = False
        self.isModified = False

        self._lastSelectedItems = []

        self._hasBeenModifiedListeners = []
        self._itemSelectedListeners = []
        self._itemsDeselectedListeners = []

        # Store callback for retrieving the nodes classes
        self.nodeClassSelector = None

        self.initUI()

        self.graphicsScene.itemSelected.connect(self.onItemSelected)
        self.graphicsScene.itemsDeselected.connect(self.onItemsDeselected)

    @property
    def isModified(self):
        return self._isModified

    @isModified.setter
    def isModified(self, value: bool):
        if not self.isModified and value:
            # Set it now, because it will be read during the next for loop.
            self._isModified = value

            # Call all registered listeners
            for callback in self._hasBeenModifiedListeners:
                callback()

        self._isModified = value

    @property
    def lastSelectedItems(self):
        return self._lastSelectedItems

    @lastSelectedItems.setter
    def lastSelectedItems(self, value: bool):
        if value != self._lastSelectedItems:
            self._lastSelectedItems = value

    # noinspection PyAttributeOutsideInit
    def initUI(self):
        self.graphicsScene = GraphicsScene(self)
        self.graphicsScene.setScene(self.sceneWidth, self.sceneHeight)

    @property
    def selectedItems(self):
        return self.graphicsScene.selectedItems()

    @property
    def view(self):
        return self.graphicsScene.views()[0]

    def onItemSelected(self):
        selectedItems = self.selectedItems
        if selectedItems != self._lastSelectedItems:
            self.lastSelectedItems = selectedItems
            self.history.store("Change selection")

            for callback in self._itemSelectedListeners:
                callback()
        self.__logger.debug("Everything done after item has been selected")

    def onItemsDeselected(self):
        self.resetLastSelectedStates()
        if self.lastSelectedItems:
            self.lastSelectedItems = []
            self.history.store("Deselect everything")

        self.__logger.debug("Everything done after all items have been deselected")

        for callback in self._itemsDeselectedListeners:
            callback()

    def addHasBeenModifiedListener(self, callback: Callable[[None], None]):
        self._hasBeenModifiedListeners.append(callback)

    def addItemSelectedListener(self, callback: Callable[[None], None]):
        self._itemSelectedListeners.append(callback)

    def addItemsDeselectedListener(self, callback: Callable[[None], None]):
        self._itemsDeselectedListeners.append(callback)

    def addDragEnterListener(self, callback: Callable[[QDragEnterEvent], None]):
        self.view.addDragEnterListener(callback)

    def addDropListener(self, callback: Callable[[QDropEvent], None]):
        self.view.addDropListener(callback)

    def resetLastSelectedStates(self):
        """"Custom flag to detect node or edge has been selected"""

        for node in self.nodes:
            node.graphicsNode.selectedState = False

        for edge in self.edges:
            edge.graphicsEdge.selectedState = False

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, nodeToRemove):
        if nodeToRemove in self.nodes:
            self.nodes.remove(nodeToRemove)
        else:
            self.__logger.warning(f"Trying to remove {nodeToRemove} from {self}.")

    def removeEdge(self, edgeToRemove):
        if edgeToRemove in self.edges:
            self.edges.remove(edgeToRemove)
        else:
            self.__logger.warning(f"Trying to remove {edgeToRemove} from {self}.")

    def clear(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        while len(self.edges) > 0:
            self.edges[0].remove()

        self.isModified = False

    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
            self.__logger.info(f"Saving to {filename} was successful.")

            self.isModified = False

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            rawData = file.read()
            try:
                data = json.loads(rawData, encoding="utf-8")
                self.deserialize(data)
                self.isModified = False
            except json.JSONDecodeError:
                raise InvalidFile(
                    f"{os.path.basename(filename)} is not a valid JSON file"
                )
            except Exception as e:
                dumpException(e)

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes:
            nodes.append(node.serialize())

        for edge in self.edges:
            edges.append(edge.serialize())

        return OrderedDict(
            [
                ("id", self.id),
                ("sceneWidth", self.sceneWidth),
                ("sceneHeight", self.sceneHeight),
                ("blocks", nodes),
                ("edges", edges),
            ]
        )

    def deserialize(self, data, hashmap=None, restoreId=True):
        if hashmap is None:
            hashmap = {}
        self.__logger.debug(f"Deserializing data: {data}")
        self.clear()

        if restoreId:
            self.id = data["id"]

        hashmap = {}

        # Create blocks
        for nodeData in data["blocks"]:
            self.getNodeClassFromData(nodeData)(self).deserialize(
                nodeData, hashmap, restoreId
            )

        # Create edges
        for edgeData in data["edges"]:
            Edge(self).deserialize(edgeData, hashmap, restoreId)
        return True

    def getNodeClassFromData(self, data):
        return Node if self.nodeClassSelector is None else self.nodeClassSelector(data)

    def setNodeClassSelector(self, classSelectingFunction):
        """"When the function self.nodeClassSelector is set, the user can use different node classes"""

        self.nodeClassSelector = classSelectingFunction

    def itemAt(self, pos):
        return self.view.itemAt(pos)


class InvalidFile(Exception):
    pass
