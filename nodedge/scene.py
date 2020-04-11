# -*- coding: utf-8 -*-
"""
Scene module containing :class:`~nodedge.scene.Scene`.
"""

import json
import logging
import os
from collections import OrderedDict
from typing import Callable, List, Optional, cast

from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtWidgets import QGraphicsItem

from nodedge.edge import Edge
from nodedge.graphics_scene import GraphicsScene
from nodedge.node import Node
from nodedge.scene_clipboard import SceneClipboard
from nodedge.scene_history import SceneHistory
from nodedge.serializable import Serializable
from nodedge.utils import dumpException


class Scene(Serializable):
    """:class:`~nodedge.scene.Scene` class"""

    def __init__(self):
        """
        :Instance Attributes:

            - **nodes** - list of `Nodes` in this `Scene`
            - **edges** - list of `Edges` in this `Scene`
            - **history** - Instance of :class:`~nodedge.scene_history.SceneHistory`
            - **clipboard** - Instance of :class:`~nodedge.scene_clipboard.SceneClipboard`
            - **scene_width** - width of this `Scene` in pixels
            - **scene_height** - height of this `Scene` in pixels
        """
        super().__init__()
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.sceneWidth = 64000
        self.sceneHeight = 64000

        self.history = SceneHistory(self)
        self.clipboard = SceneClipboard(self)

        self._isModified: bool = False
        self.isModified = False

        self._lastSelectedItems = []

        self._hasBeenModifiedListeners = []
        self._itemSelectedListeners = []
        self._itemsDeselectedListeners = []

        self._silentSelectionEvents = False

        # Store callback for retrieving the nodes classes
        self.nodeClassSelector = None

        self.graphicsScene = GraphicsScene(self)
        self.graphicsScene.setScene(self.sceneWidth, self.sceneHeight)
        self.graphicsScene.itemSelected.connect(self.onItemSelected)
        self.graphicsScene.itemsDeselected.connect(self.onItemsDeselected)

    @property
    def isModified(self) -> bool:
        """
        Has this `Scene` been modified?

        :getter: ``True`` if the `Scene` has been modified
        :setter: set new state. Triggers `Has Been Modified` event
        :type: ``bool``
        """

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

    @property
    def selectedItems(self) -> List[QGraphicsItem]:
        """
        Returns currently selected Graphics Items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """

        return cast(List[QGraphicsItem], self.graphicsScene.selectedItems())

    @property
    def view(self):
        """Shortcut for returning `Scene` ``QGraphicsView``

        :return: ``QGraphicsView`` attached to the `Scene`
        :rtype: ``QGraphicsView``
        """
        return self.graphicsScene.views()[0]

    @property
    def silentSelectionEvents(self):
        """"
        If this property is true, do not trigger onItemSelected when an item is selected

        :return: True is onItemSelected is not triggered when an item is selected
        :rtype: ``bool``
        """
        return self._silentSelectionEvents

    @silentSelectionEvents.setter
    def silentSelectionEvents(self, value: bool):
        if self._silentSelectionEvents != value:
            self._silentSelectionEvents = value

    def onItemSelected(self, silent: bool = False):
        """
        Handle Item selection and trigger event `Item Selected`

        :param silent: If ``True`` scene's onItemSelected won't be called and history stamp not stored
        :type silent: ``bool``
        """
        if self._silentSelectionEvents:
            return

        selectedItems = self.selectedItems
        if selectedItems != self._lastSelectedItems:
            self.lastSelectedItems = selectedItems

            if not silent:
                self.history.store("Change selection")
                for callback in self._itemSelectedListeners:
                    callback()

    def onItemsDeselected(self, silent: bool = False):
        """
        Handle Items deselection and trigger event `Items Deselected`

        :param silent: If ``True`` scene's onItemsDeselected won't be called and history stamp not stored
        :type silent: ``bool``
        """
        self.resetLastSelectedStates()
        if self.lastSelectedItems:
            self.lastSelectedItems = []

            if not silent:
                self.history.store("Deselect everything")
                for callback in self._itemsDeselectedListeners:
                    callback()

    def doDeselectItems(self, silent: bool = False) -> None:
        """
        Deselects everything in scene

        :param silent: If ``True`` scene's onItemsDeselected won't be called
        :type silent: ``bool``
        """
        for item in self.selectedItems:
            item.setSelected(False)
        if not silent:
            self.onItemsDeselected()

    def addHasBeenModifiedListener(self, callback: Callable[[], None]):
        """
        Register callback for `Has Been Modified` event

        :param callback: callback function
        :type callback: ``Callable[[], None]``
        """
        self._hasBeenModifiedListeners.append(callback)

    def addItemSelectedListener(self, callback: Callable[[], None]):
        """
        Register callback for `Item Selected` event

        :param callback: callback function
        :type callback: ``Callable[[], None]``
        """
        self._itemSelectedListeners.append(callback)

    def addItemsDeselectedListener(self, callback: Callable[[], None]):
        """
        Register callback for `Items Deselected` event

        :param callback: callback function
        """
        self._itemsDeselectedListeners.append(callback)

    def addDragEnterListener(self, callback: Callable[[QDragEnterEvent], None]):
        """
        Register callback for `Drag Enter` event

        :param callback: callback function
        """
        self.view.addDragEnterListener(callback)

    def addDropListener(self, callback: Callable[[QDropEvent], None]):
        """
        Register callback for `Drop` event

        :param callback: callback function
        """
        self.view.addDropListener(callback)

    def resetLastSelectedStates(self):
        """Resets internal `selected flags` in all `Nodes` and `Edges` in the `Scene`"""

        for node in self.nodes:
            node.graphicsNode.selectedState = False

        for edge in self.edges:
            edge.graphicsEdge.selectedState = False

    def addNode(self, node: Node):
        """Add :class:`~nodedge.node.Node` to this `Scene`

        :param node: :class:`~nodedge.node.Node` to be added to this `Scene`
        :type node: :class:`~nodedge.node.Node`
        """
        self.nodes.append(node)

    def addEdge(self, edge: Edge):
        """Add :class:`~nodedge.edge.Edge` to this `Scene`

        :param edge: :class:`~nodedge.edge.Edge` to be added to this `Scene`
        :return: :class:`~nodedge.edge.Edge`
        """
        self.edges.append(edge)

    def removeNode(self, nodeToRemove: Node):
        """Remove :class:`~nodedge.node.Node` from this `Scene`
        :param nodeToRemove: :class:`~nodedge.node.Node` to be removed from this `Scene`
        :type nodeToRemove: :class:`~nodedge.node.Node`
        """
        if nodeToRemove in self.nodes:
            self.nodes.remove(nodeToRemove)
        else:
            self.__logger.warning(
                f"Trying to remove {nodeToRemove} from {self} but is it not in the node list."
            )

    def removeEdge(self, edgeToRemove: Edge):
        """Remove :class:`~nodedge.edge.Edge` from this `Scene`

        :param edgeToRemove: :class:`~nodedge.edge.Edge` to be remove from this `Scene`
        :return: :class:`~nodedge.edge.Edge`
        """
        if edgeToRemove in self.edges:
            self.edges.remove(edgeToRemove)
        else:
            self.__logger.warning(
                f"Trying to remove {edgeToRemove} from {self} but is it not is the edge list."
            )

    def clear(self):
        """Remove all `Nodes` from this `Scene`. This causes also to remove all `Edges`"""
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        while len(self.edges) > 0:
            self.edges[0].remove()

        self.isModified = False

    def saveToFile(self, filename):
        """
        Save this `Scene` to the file on disk.

        :param filename: where to save this scene
        :type filename: ``str``
        """
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
            self.__logger.info(f"Saving to {filename} was successful.")

            self.isModified = False

    def loadFromFile(self, filename):
        """
        Load `Scene` from a file on disk

        :param filename: from what file to load the `Scene`
        :type filename: ``str``
        :raises: :class:`~nodedge.scene.InvalidFile` if there was an error decoding JSON file
        """
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

    def serialize(self) -> OrderedDict:
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
                ("nodes", nodes),
                ("edges", edges),
            ]
        )

    def deserialize(
        self, data: dict, hashmap: Optional[dict] = None, restoreId: bool = True
    ) -> bool:
        if hashmap is None:
            hashmap = {}
        self.__logger.debug(f"Deserialize data: {data}")
        self.clear()

        if restoreId:
            self.id = data["id"]

        # Create blocks
        for nodeData in data["nodes"]:
            self.getNodeClassFromData(nodeData)(self).deserialize(
                nodeData, hashmap, restoreId
            )

        # Create edges
        for edgeData in data["edges"]:
            Edge(self).deserialize(edgeData, hashmap, restoreId)
        return True

    def getNodeClassFromData(self, data):
        """
        Takes `Node` serialized data and determines which `Node Class` to instantiate according the description
        in the serialized Node.

        :param data: serialized `Node` object data
        :type data: ``dict``
        :return: Instance of `Node` class to be used in this Scene
        :rtype: `Node` class instance
        """
        return Node if self.nodeClassSelector is None else self.nodeClassSelector(data)

    def setNodeClassSelector(self, classSelectingFunction):
        """
        Set the function which decides what `Node` class to instantiate during `Scene` deserialization.
        If not set, we will always instantiate :class:`~nodedge.node.Node` for each `Node` in the `Scene`

        :param classSelectingFunction: function which returns `Node` class type (not instance)
                                       from `Node` serialized ``dict`` data
        :type classSelectingFunction: ``function``
        :return: Class Type of `Node` to be instantiated during deserialization
        :rtype: `Node` class type
        """
        self.nodeClassSelector = classSelectingFunction

    def itemAt(self, pos):
        """Shortcut for retrieving item at provided `Scene` position

        :param pos: scene position
        :type pos: ``QPointF``
        :return: Qt Graphics Item at scene position
        :rtype: ``QGraphicsItem``
        """
        return self.view.itemAt(pos)


class InvalidFile(Exception):
    pass
