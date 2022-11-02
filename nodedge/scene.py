# -*- coding: utf-8 -*-
"""
Scene module containing :class:`~nodedge.scene.Scene`.
"""

import json
import os
from collections import OrderedDict
from typing import Callable, List, Optional, cast

from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QGraphicsItem

from nodedge.edge import Edge
from nodedge.elements.comment_element import CommentElement
from nodedge.elements.element import Element
from nodedge.graphics_node import GraphicsNode
from nodedge.graphics_scene import GraphicsScene
from nodedge.graphics_view import GraphicsView
from nodedge.logger import logger
from nodedge.node import Node
from nodedge.scene_clipboard import SceneClipboard
from nodedge.scene_coder import SceneCoder
from nodedge.scene_history import SceneHistory
from nodedge.serializable import Serializable
from nodedge.utils import dumpException


class Scene(Serializable):
    """:class:`~nodedge.scene.Scene` class"""

    def __init__(self) -> None:
        """
        :Instance Attributes:

            - **nodes** - list of `Nodes` in this `Scene`
            - **edges** - list of `Edges` in this `Scene`
            - **history** - Instance of :class:`~nodedge.scene_history.SceneHistory`
            - **clipboard** - Instance of
                :class:`~nodedge.scene_clipboard.SceneClipboard`
            - **scene_width** - width of this `Scene` in pixels
            - **scene_height** - height of this `Scene` in pixels
        """
        super().__init__()
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.elements: List[Element] = []

        self.sceneWidth: int = 64000
        self.sceneHeight: int = 64000

        self.history: SceneHistory = SceneHistory(self)
        self.clipboard: SceneClipboard = SceneClipboard(self)
        self.coder: SceneCoder = SceneCoder(scene=self)

        self._isModified: bool = False
        self.isModified: bool = False

        self._lastSelectedItems: List[QGraphicsItem] = []

        self._hasBeenModifiedListeners: List[Callable] = []
        self._itemSelectedListeners: List[Callable] = []
        self._itemsDeselectedListeners: List[Callable] = []

        self._silentSelectionEvents: bool = False

        # Store callback for retrieving the nodes classes
        self.nodeClassSelector = None

        self.graphicsScene: GraphicsScene = GraphicsScene(self)
        self.graphicsScene.setScene(self.sceneWidth, self.sceneHeight)
        self.graphicsScene.itemSelected.connect(self.onItemSelected)

        # current filename assigned to this scene
        self.filename: Optional[str] = None

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
    def lastSelectedItems(self) -> List[QGraphicsItem]:
        """
        Returns last selected graphics items.
        This property is used to detect if selection has changed.

        :return: Last selected items
        :rtype: ``list[QGraphicsItem]``
        """
        return self._lastSelectedItems

    @lastSelectedItems.setter
    def lastSelectedItems(self, value: List[QGraphicsItem]):
        if value != self._lastSelectedItems:
            self._lastSelectedItems = value

    @property
    def selectedItems(self) -> List[QGraphicsItem]:
        """
        Returns currently selected Graphics Items

        :return: list of ``QGraphicsItems``
        :rtype: list[QGraphicsItem]
        """

        return self.graphicsScene.selectedItems()

    @property
    def selectedNode(self) -> Optional[Node]:
        ret = None
        if len(self.selectedItems) == 1:
            if isinstance(self.selectedItems[0], GraphicsNode):
                ret = self.selectedItems[0].node

        return ret

    @property
    def selectedNodes(self) -> List[GraphicsNode]:
        return [item for item in self.selectedItems if isinstance(item, GraphicsNode)]

    @property
    def graphicsView(self) -> GraphicsView:
        """Shortcut for returning `Scene` ``QGraphicsView``

        :return: ``QGraphicsView`` attached to the `Scene`
        :rtype: ``QGraphicsView``
        """
        return cast(GraphicsView, self.graphicsScene.views()[0])

    @property
    def silentSelectionEvents(self):
        """ "
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

        :param silent: If ``True`` scene's onItemSelected won't be called and history
            stamp not stored.
        :type silent: ``bool``
        """
        if self._silentSelectionEvents:
            return

        selectedItems = self.selectedItems
        if selectedItems != self._lastSelectedItems:
            self.lastSelectedItems = selectedItems

            if not silent:
                # we could create some kind of UI which could be serialized,
                # therefore first run all callbacks...
                for callback in self._itemSelectedListeners:
                    callback()
                # and store history as a last step always
                self.history.store("Change selection")

    def onItemsDeselected(self, silent: bool = False):
        """
        Handle Items deselection and trigger event `Items Deselected`

        :param silent: If ``True`` scene's onItemsDeselected won't be called and
            history stamp not stored.
        :type silent: ``bool``
        """

        if self.selectedItems == self.lastSelectedItems:
            return

        self.resetLastSelectedStates()
        if not self.selectedItems:
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
        self.graphicsView.addDragEnterListener(callback)

    def addDropListener(self, callback: Callable[[QDropEvent], None]):
        """
        Register callback for `Drop` event

        :param callback: callback function
        """
        self.graphicsView.addDropListener(callback)

    def resetLastSelectedStates(self) -> None:
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

    def addElement(self):
        element = CommentElement(self)
        logger.info(f"Number of elements: {len(self.elements)}")
        logger.info([e.graphicsElement.pos() for e in self.elements])

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
            logger.warning(
                f"Trying to remove {nodeToRemove} from {self} but is it not in the "
                f"node list. "
            )

    def removeElement(self, elementToRemove: Element):
        """Remove :class:`~nodedge.node.Node` from this `Scene`
        :param elementToRemove: :class:`~nodedge.elements.element.Element` to be removed from this `Scene`
        :type elementToRemove: :class:`~nodedge.elements.element.Element`
        """
        if elementToRemove in self.elements:
            self.elements.remove(elementToRemove)
        else:
            logger.warning(
                f"Trying to remove {elementToRemove} from {self} but is it not in the "
                f"element list. "
            )

    def removeEdge(self, edgeToRemove: Edge):
        """Remove :class:`~nodedge.edge.Edge` from this `Scene`

        :param edgeToRemove: :class:`~nodedge.edge.Edge` to be remove from this `Scene`
        :return: :class:`~nodedge.edge.Edge`
        """
        if edgeToRemove in self.edges:
            self.edges.remove(edgeToRemove)
        else:
            logger.warning(
                f"Trying to remove {edgeToRemove} from {self} but is it not is the "
                f"edge list. "
            )

    def clear(self) -> None:
        """Remove all `Nodes` from this `Scene`. This causes also to remove all
        `Edges`"""
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
            logger.info(f"Saving to {filename} was successful.")

            self.isModified = False
            self.filename = filename

    def loadFromFile(self, filename: str) -> None:
        """
        Load `Scene` from a file on disk

        :param filename: from what file to load the `Scene`
        :type filename: ``str``
        :raises: :class:`~nodedge.scene.InvalidFile` if there was an error
            decoding JSON file.
        """
        with open(filename) as file:
            rawData = file.read()
            try:
                data = json.loads(rawData)
                self.deserialize(data)
                self.isModified = False
                self.filename = filename
            except json.JSONDecodeError:
                raise InvalidFile(
                    f"{os.path.basename(filename)} is not a valid JSON file"
                )
            except Exception as e:
                dumpException(e)

    def serialize(self) -> OrderedDict:
        """
        Serialization method to serialize this class data into ``OrderedDict`` which
        can be stored in memory or file easily.

        :return: data serialized in ``OrderedDict``
        :rtype: ``OrderedDict``
        """
        nodes, edges, elements = [], [], []
        for node in self.nodes:
            nodes.append(node.serialize())

        for edge in self.edges:
            edges.append(edge.serialize())

        for element in self.elements:
            elements.append(element.serialize())

        return OrderedDict(
            [
                ("id", self.id),
                ("sceneWidth", self.sceneWidth),
                ("sceneHeight", self.sceneHeight),
                ("nodes", nodes),
                ("edges", edges),
                ("elements", elements),
            ]
        )

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = True,
        *args,
        **kwargs,
    ) -> bool:
        """
        Deserialization method which take data in python ``dict`` format with helping
        `hashmap` containing references to existing entities.

        :param data: dictionary containing serialized data
        :type data: ``dict``
        :param hashmap: helper dictionary containing references (by id == key) to
            existing objects
        :type hashmap: ``dict``
        :param restoreId: ``True`` if we are creating new sockets. ``False`` is useful
            when loading existing sockets which we want to keep the existing
            object's `id`
        :type restoreId: ``bool``
        :return: ``True`` if deserialization was successful, ``False`` otherwise
        :rtype: ``bool``
        """
        try:
            if hashmap is None:
                hashmap = {}
            logger.debug(f"Deserialize data: {data}")
            self.clear()

            if restoreId:
                self.id = data["id"]

            # Deserialize blocks
            allNodes = self.nodes.copy()

            for nodeData in data["nodes"]:
                # Does this node already exist in the scene?
                existingNode: Optional[Node] = None
                for node in allNodes:
                    if node.id == nodeData["id"]:
                        existingNode = node

                if not existingNode:
                    newNode = self.getNodeClassFromData(nodeData)(self)
                    newNode.deserialize(nodeData, hashmap, restoreId)
                else:
                    existingNode.deserialize(nodeData, hashmap, restoreId)

            # Remove nodes which are left in the scene and were not
            # in the serialized data. They were not in the graph before.
            while allNodes:
                node = allNodes.pop()
                node.remove()

            # Deserialize edges
            allEdges = self.edges.copy()

            for edgeData in data["edges"]:
                # Does this edge already exist in the scene?
                existingEdge: Optional[Edge] = None
                for edge in allEdges:
                    if edge.id == edgeData["id"]:
                        existingEdge = edge

                if not existingEdge:
                    Edge(self).deserialize(edgeData, hashmap, restoreId)
                else:
                    existingEdge.deserialize(edgeData, hashmap, restoreId)

            # Remove edge which are left in the scene and were not
            # in the serialized data. They were not in the graph before.
            while allEdges:
                edge = allEdges.pop()
                edge.remove()

            allElements = self.elements.copy()
            elementsData = data.get("elements")
            if elementsData is not None:
                for elementData in elementsData:
                    existingElement: Optional[Element] = None
                    for element in allElements:
                        if element.id == elementData["id"]:
                            existingElement = element

                    if not existingElement:
                        CommentElement(self).deserialize(
                            elementData, hashmap, restoreId
                        )

                while allElements:
                    element = allElements.pop()
                    element.remove()
            return True
        except Exception as e:

            dumpException(e)
            return False

    def getNodeClassFromData(self, data):
        """
        Takes :class:`~nodedge.node.Node` serialized data and determines which `Node
        Class` to instantiate according the description in the serialized Node.

        :param data: serialized :class:`~nodedge.node.Node` object data
        :type data: ``dict``
        :return: Instance of :class:`~nodedge.node.Node` class to be used in this Scene
        :rtype: :class:`~nodedge.node.Node` class instance
        """
        return Node if self.nodeClassSelector is None else self.nodeClassSelector(data)

    def setNodeClassSelector(self, classSelectingFunction):
        """
        Set the function which decides what :class:`~nodedge.node.Node` class to
        instantiate during `Scene` deserialization. If not set, we will always
        instantiate :class:`~nodedge.node.Node` for each :class:`~nodedge.node.Node`
        in the `Scene`

        :param classSelectingFunction: function which returns
            :class:`~nodedge.node.Node` class type (not instance) from
            :class:`~nodedge.node.Node` serialized ``dict`` data
        :type classSelectingFunction: ``function``
        :return: Class Type of :class:`~nodedge.node.Node` to be instantiated during
            deserialization
        :rtype: :class:`~nodedge.node.Node` class type
        """
        self.nodeClassSelector = classSelectingFunction

    def itemAt(self, pos):
        """Shortcut for retrieving item at provided `Scene` position

        :param pos: scene position
        :type pos: ``QPointF``
        :return: Qt Graphics Item at scene position
        :rtype: ``QGraphicsItem``
        """
        return self.graphicsView.itemAt(pos)

    def getNodeById(self, nodeId: int) -> Optional[Node]:
        """
        Find node in the scene according to provided `nodeId`

        :param nodeId: ID of the node we are looking for
        :type nodeId: ``int``
        :return: Found `:class:`~nodedge.node.Node`` or ``None``
        :rtype: `:class:`~nodedge.node.Node`` or ``None``
        """
        for node in self.nodes:
            if node.id == nodeId:
                return node
        return None


class InvalidFile(Exception):
    pass
