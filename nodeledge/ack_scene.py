import json
import logging

from collections import OrderedDict
from nodeledge.ack_serializable import AckSerializable
from nodeledge.ack_node import AckNode
from nodeledge.ack_edge import AckEdge
from nodeledge.ack_scene_history import AckSceneHistory
from nodeledge.ack_scene_clipboard import AckSceneClipboard

from nodeledge.ack_graphics_scene import AckGraphicsScene


class AckScene(AckSerializable):
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.edges = []

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.sceneWidth = 64000
        self.sceneHeight = 64000

        self.history = AckSceneHistory(self)
        self.clipboard = AckSceneClipboard(self)

        self._hasBeenModified = False
        self.hasBeenModified = False
        self._hasBeenModifiedListeners = []

        self.initUI()

    @property
    def hasBeenModified(self):
        return False
        # return self._hasBeenModified

    @hasBeenModified.setter
    def hasBeenModified(self, value):
        if not self.hasBeenModified and value:
            self._hasBeenModified = value

            # Call all registered listeners
            for callback in self._hasBeenModifiedListeners:
                callback()

        self._hasBeenModified = value

    def addHasBeenModifiedListener(self, callback):
        self._hasBeenModifiedListeners.append(callback)

    def initUI(self):
        self.graphicsScene = AckGraphicsScene(self)
        self.graphicsScene.setScene(self.sceneWidth, self.sceneHeight)

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

        self.hasBeenModified = False

    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
            self.__logger.info(f"Saving to {filename} was successful.")

            self.hasBeenModified = False

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            rawData = file.read()
            data = json.loads(rawData, encoding="utf-8")
            self.deserialize(data)

            self.hasBeenModified = False

    def serialize(self):
        nodes, edges = [], []
        for node in self.nodes:
            nodes.append(node.serialize())

        for edge in self.edges:
            edges.append(edge.serialize())

        return OrderedDict([("id",  self.id),
                            ("sceneWidth", self.sceneWidth),
                            ("sceneHeight", self.sceneHeight),
                            ("nodes", nodes),
                            ("edges", edges)
                            ])

    def deserialize(self, data, hashmap={}, restoreId=True):
        self.__logger.debug(f"Deserializing data: {data}")
        self.clear()

        if restoreId:
            self.id = data["id"]

        hashmap = {}

        # Create nodes
        for nodeData in data["nodes"]:
            AckNode(self).deserialize(nodeData, hashmap, restoreId)

        # Create edges
        for edgeData in data["edges"]:
            AckEdge(self).deserialize(edgeData, hashmap, restoreId)
        return True