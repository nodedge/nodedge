# -*- coding: utf-8 -*-
"""
Node module containing :class:`~nodedge.node.Node` class.
"""


import logging
from collections import OrderedDict
from typing import Collection, List, Optional, Tuple, TypeVar

from PyQt5.QtCore import QPoint, QPointF

from nodedge.edge import Edge
from nodedge.graphics_node import GraphicsNode
from nodedge.node_content import NodeContent
from nodedge.serializable import Serializable
from nodedge.socket import Socket, SocketLocation
from nodedge.utils import dumpException

Pos = TypeVar("Pos", List, Tuple, QPoint, QPointF)


class Node(Serializable):
    """:class:`~nodedge.node.Node` class representing a node in the `Scene`."""

    def __init__(
        self,
        scene: "Scene",  # type: ignore
        title: str = "Undefined node",
        inputSocketTypes: Collection[int] = (),
        outputSocketTypes: Collection[int] = (),
    ):
        """
        :param scene: reference to the :class:`~nodedge.scene.Scene`
        :type scene: :class:`~nodedge.scene.Scene`
        :param title: node title shown in scene
        :type title: ``str``
        :param inputSocketTypes: list of types of the input `Sockets`
        :type inputSocketTypes: ``Collection[int]``
        :param outputSocketTypes: list of types of the output `Sockets`
        :type outputSocketTypes: ``Collection[int]``
        """

        super().__init__()
        self._title: str = title
        self.scene: "Scene" = scene  # type: ignore

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.initInnerClasses()
        self.initSettings()

        self.scene.addNode(self)
        self.scene.graphicsScene.addItem(self.graphicsNode)

        self.inputSockets: List[Socket] = []
        self.outputSockets: List[Socket] = []
        self.initSockets(inputSocketTypes, outputSocketTypes)

        # Evaluation attributes
        self._isDirty: bool = False
        self._isInvalid: bool = False

    def __str__(self):
        return f"0x{hex(id(self))[-4:]} Node({self.title}, {self.inputSockets}, {self.outputSockets})"

    # noinspection PyAttributeOutsideInit
    def initInnerClasses(self) -> None:
        """
        Set up graphics node and content widget.
        """
        self.content: NodeContent = NodeContent(self)
        self.graphicsNode: GraphicsNode = GraphicsNode(self)

    # noinspection PyAttributeOutsideInit
    def initSettings(self) -> None:
        """
        Initialize properties and sockets information.
        """
        self.title: str = self._title
        self._socketSpacing: int = 22
        self._inputSocketPosition: SocketLocation = SocketLocation.LEFT_TOP
        self._outputSocketPosition: SocketLocation = SocketLocation.RIGHT_BOTTOM
        self._inputAllowsMultiEdges: bool = False
        self._outputAllowsMultiEdges: bool = True

    def initSockets(
        self, inputs: Collection[int], outputs: Collection[int], reset: bool = True
    ) -> None:
        """
        Create input and output sockets.

        :param inputs: list of types of the input `Sockets`. Every type is associated with a ``int``
        :type inputs: ``Collection[int]``
        :param outputs: list of types of the input `Sockets`
        :type outputs: ``Collection[int]``
        :param reset: if ``True`` destroy and remove old `Sockets`
        :type reset: ``bool``
        """
        if reset and hasattr(self, "inputs") and hasattr(self, "outputs"):
            for socket in self.inputSockets + self.outputSockets:
                self.scene.graphicsScene.removeItem(socket.graphicsSocket)
            self.inputSockets = []
            self.outputSockets = []

        # Create new sockets
        for ind, inp in enumerate(inputs):
            socket = Socket(
                node=self,
                index=ind,
                location=self._inputSocketPosition,
                socketType=inp,
                allowsMultiEdges=self._inputAllowsMultiEdges,
                countOnThisNodeSide=len(inputs),
                isInput=True,
            )
            self.inputSockets.append(socket)

        for ind, out in enumerate(outputs):
            socket = Socket(
                node=self,
                index=ind,
                location=self._outputSocketPosition,
                socketType=out,
                allowsMultiEdges=self._outputAllowsMultiEdges,
                countOnThisNodeSide=len(outputs),
                isInput=False,
            )
            self.outputSockets.append(socket)

    def onEdgeConnectionChanged(self, newEdge: Edge) -> None:
        """
        Handle event associated with a change in any of the connections (`Edge`). Currently unused.

        :param newEdge: reference to the changed :class:`~nodedge.edge.Edge`
        :type newEdge: :class:`~nodedge.edge.Edge`
        """
        self.__logger.debug(f"{newEdge}")

    def onInputChanged(self, newEdge: Edge):
        """
        Handle event associated with a change in this node's input edge. When it happens, this node and all
        its descendants are labelled as dirty.

        :param newEdge: reference to the changed :class:`~nodedge.edge.Edge`
        :type newEdge: :class:`~nodedge.edge.Edge`
        """

        self.__logger.debug(f"{newEdge}")
        self.isDirty = True
        self.markDescendantsDirty()

    @property
    def title(self) -> str:
        """
        Title shown in the scene.

        :getter: return current node title
        :setter: set node title and pass it to the graphical node
        :rtype: ``str``
        """
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        self._title = value
        self.graphicsNode.title = value

    @property
    def pos(self):
        """
        Retrieve node's position in the scene

        :return: node position
        :rtype: ``QPointF``
        """
        return self.graphicsNode.pos()  # QPointF

    @pos.setter
    def pos(self, pos: Pos):
        if isinstance(pos, (list, tuple)):
            try:
                x, y = pos
                self.graphicsNode.setPos(x, y)

            except ValueError:
                raise ValueError("Pass an iterable with two numbers.")
            except TypeError:
                raise TypeError("Pass an iterable with two numbers.")
        elif isinstance(pos, QPointF):
            self.graphicsNode.setPos(pos)

    @property
    def isDirty(self):
        """
        Property stating whether or not this node is marked as `Dirty`, i.e. the node has not been
        evaluated since last node's input/output change.

        :getter: ``True`` if this node is marked as `Dirty`, ``False`` otherwise
        :setter: set the dirtiness status of this node
        :type: ``bool``
        """
        return self._isDirty

    @isDirty.setter
    def isDirty(self, value: bool):
        if self._isDirty != value:
            self._isDirty = value

        if self._isDirty:
            self.onMarkedDirty()

    @property
    def isInvalid(self):
        """
        Property stating whether or not this node is marked as `Invalid`, i.e. the node has been
        evaluated since last node's input/output change, but the evaluation was inconsistent.

        :getter: ``True`` if this node is marked as `Invalid`,
            ``False`` otherwise
        :setter: set the validity status of this node
        :type: ``bool``
        """
        return self._isInvalid

    @isInvalid.setter
    def isInvalid(self, value: bool):
        if self._isInvalid != value:
            self._isInvalid = value

        if self._isInvalid:
            self.onMarkedInvalid()

    @property
    def isSelected(self):
        """
        Retrieve graphics node selection status
        """
        return self.graphicsNode.isSelected()

    @isSelected.setter
    def isSelected(self, value: bool):
        self.graphicsNode.setSelected(value)
        self.graphicsNode._lastSelectedState = value
        if value is True:
            self.graphicsNode.onSelected()

    def socketPos(self, index: int, position: int, countOnThisSide: int = 1) -> QPointF:
        """
        Get the relative `x, y` position of a :class:`~nodedge.socket.Socket`. This is used for placing
        the `Graphics Sockets` on `Graphics Node`.

        :param index: Order number of the Socket. (0, 1, 2, ...)
        :type index: ``int``
        :param position: `Socket Position Constant` describing where the Socket is located
        :type position: :class:`~nodedge.socket.SocketLocation`
        :param countOnThisSide: Total number of Sockets on this `Socket Position`
        :type countOnThisSide: ``int``
        :return: Position of described Socket on the `Node`
        :rtype: ``QPointF``
        """
        x: int = (
            0
            if (
                position
                in (
                    SocketLocation.LEFT_TOP,
                    SocketLocation.LEFT_CENTER,
                    SocketLocation.LEFT_BOTTOM,
                )
            )
            else self.graphicsNode.width
        )

        if position in (SocketLocation.LEFT_BOTTOM, SocketLocation.RIGHT_BOTTOM):
            y: float = (
                self.graphicsNode.height
                - self.graphicsNode.edgeRoundness
                - self.graphicsNode.titleVerticalPadding
                - index * self._socketSpacing
            )
        elif position in (SocketLocation.LEFT_CENTER, SocketLocation.RIGHT_CENTER):
            numberOfSockets: int = countOnThisSide
            nodeHeight: float = self.graphicsNode.height
            topOffset: float = (
                self.graphicsNode.titleHeight
                + 2 * self.graphicsNode.titleVerticalPadding
            )
            availableHeight: float = nodeHeight - topOffset

            # TODO: use total height of all sockets
            # totalHeightOfAllSockets = numberOfSockets * self._socketSpacing

            # TODO: use newTop in node
            # newTop = availableHeight - totalHeightOfAllSockets

            y = topOffset + availableHeight / 2.0 + (index - 0.5) * self._socketSpacing
            if numberOfSockets > 1:
                y -= self._socketSpacing * (numberOfSockets - 1) / 2

        elif position in (SocketLocation.LEFT_TOP, SocketLocation.RIGHT_TOP):
            y = (
                self.graphicsNode.titleHeight
                + self.graphicsNode.titleVerticalPadding
                + self.graphicsNode.edgeRoundness
                + index * self._socketSpacing
            )
        else:
            y = 0

        return QPointF(x, y)

    def updateConnectedEdges(self):
        """
        Refresh positions of all connected `Edges`.
        It is used for updating graphical edges.
        """
        for socket in self.inputSockets + self.outputSockets:
            for edge in socket.edges:
                self.__logger.debug("Updating socket edges.")
                edge.updatePos()
            else:
                self.__logger.debug("No edge is connected.")

    # noinspection PyAttributeOutsideInit
    def remove(self):
        """
        Safely remove this node.
        """
        self.__logger.debug(f"Removing {self}")
        self.__logger.debug("Removing all edges connected to the node.")
        for socket in self.inputSockets + self.outputSockets:
            socket.removeAllEdges()
        self.__logger.debug("Removing the graphical node.")
        self.scene.graphicsScene.removeItem(self.graphicsNode)
        self.graphicsNode = None
        self.__logger.debug("Removing the node from the scene.")
        self.scene.removeNode(self)

    def onMarkedDirty(self):
        """
        Called when this `Node` has been marked as `Dirty`.
        This method must be overridden.
        """
        pass

    def markChildrenDirty(self, newValue: bool = True) -> None:
        """
        Mark the children of this node to be `Dirty`. Children are first-level descendants.
        Note: it does not apply to this node.
        :param new_value: ``True`` if children should be `Dirty`, ``False`` to un-dirty them.
        :type new_value: ``bool``
        """
        for otherNode in self.getChildrenNodes():
            otherNode.isDirty = newValue

    def markDescendantsDirty(self, newValue: bool = True) -> None:
        """
        Mark all-level descendants of this `Node` to be `Dirty`.
         Note: it does not apply to this node.

        :param newValue: ``True`` if descendants should be `Dirty`,
            ``False`` to un-dirty them.
        :type newValue: ``bool``
        """
        for otherNode in self.getChildrenNodes():
            otherNode.isDirty = newValue
            otherNode.markChildrenDirty(newValue)

    def onMarkedInvalid(self) -> None:
        """
        Called when this node has been marked as `Invalid`.
        This method must be overridden.
        """
        pass

    def markChildrenInvalid(self, newValue: bool = True) -> None:
        """
        Mark children of this node as `Invalid`. Children are first-level descendants.
        Note: it does not apply to this node.

        :param new_value: ``True`` if children should be `Invalid`, ``False`` to make them valid.
        :type new_value: ``bool``
        """
        for otherNode in self.getChildrenNodes():
            otherNode.isInvalid = newValue

    def markDescendantsInvalid(self, newValue: bool = True) -> None:
        """
        Mark descendants of this node as `Invalid`.
        Note: it does not apply to this node.

        :param new_value: ``True`` if descendants should be `Invalid`,
            ``False`` to make descendants valid.
        :type new_value: ``bool``
        """

        for otherNode in self.getChildrenNodes():
            otherNode.isInvalid = newValue
            otherNode.markChildrenInvalid(newValue)

    def eval(self) -> float:
        """
        Evaluate this node.
        This must be overridden.
        See :ref:`evaluation` for more details.
        """
        self.isDirty = False
        self.isInvalid = False
        return 0

    def evalChildren(self) -> None:
        """
        Evaluate children of this node
        """
        for node in self.getChildrenNodes():
            # TODO: Investigate if we want to evaluate all the children of the child
            node.eval()

    def getChildrenNodes(self) -> List["Node"]:
        """
        Retrieve all children connected to this node outputs.

        :return: list of `Nodes` connected to this node from all outputs
        :rtype: List[:class:`~nodedge.node.Node`]
        """
        if not self.outputSockets:
            return []

        otherNodes = []
        for outputSocket in self.outputSockets:
            for edge in outputSocket.edges:
                otherNode = edge.getOtherSocket(outputSocket).node
                otherNodes.append(otherNode)

        return otherNodes

    def __IONodesAt(self, side: str, index: int) -> List["Node"]:
        IONodes = []
        if side == "input":
            socketList = self.inputSockets
        elif side == "output":
            socketList = self.outputSockets
        else:
            raise ValueError("Side is either 'input' or 'output'")

        try:
            socket = socketList[index]
            for edge in socket.edges:
                otherSocket = edge.getOtherSocket(socket)
                IONodes.append(otherSocket.node)
        except IndexError:
            self.__logger.warning(
                f"Trying to get connected {side} node at #{index} "
                f"but {self} has only {len(socketList)} outputs."
            )
        except Exception as e:
            dumpException(e)
        finally:
            return IONodes

    def inputNodesAt(self, index: int) -> List["Node"]:
        """
        Get **all** nodes connected to the input specified by `index`.

        :param index: order number of the input socket
        :type index: ``int``
        :return: all :class:`~nodedge.node.Node` instances which are connected to the specified input
            or ``[]`` if there is no connection or index is out of range
        :rtype: List[:class:`~nodedge.node.Node`]
        """
        return self.__IONodesAt("input", index)

    def inputNodeAt(self, index: int) -> Optional["Node"]:
        """
        Get the **first**  node connected to the  input specified by `index`.

        :param index: order number of the input socket
        :type index: ``int``
        :return: :class:`~nodedge.node.Node` which is connected to the specified input
            or ``None`` if there is no connection or index is out of range
        :rtype: :class:`~nodedge.node.Node`
        """

        try:
            return self.inputNodesAt(index)[0]
        except IndexError:
            # Index Error has already been caught in inputNodesAt, do not log it again.
            return None
        except Exception as e:
            dumpException(e)
        return None

    def outputNodesAt(self, index: int) -> List["Node"]:
        """
        Get **all** nodes connected to the output specified by `index`.

        :param index: order number of the output socket
        :type index: ``int``
        :return: all :class:`~nodedge.node.Node` instances which are connected to the specified output
            or ``[]`` if there is no connection or index is out of range
        :rtype: List[:class:`~nodedge.node.Node`]
        """
        return self.__IONodesAt("output", index)

    def serialize(self) -> OrderedDict:
        inputs, outputs = [], []
        for socket in self.inputSockets:
            inputs.append(socket.serialize())
        for socket in self.outputSockets:
            outputs.append(socket.serialize())

        return OrderedDict(
            [
                ("id", self.id),
                ("title", self.title),
                ("posX", self.graphicsNode.scenePos().x()),
                ("posY", self.graphicsNode.scenePos().y()),
                ("inputs", inputs),
                ("outputs", outputs),
                ("content", self.content.serialize()),
            ]
        )

    def deserialize(self, data, hashmap=None, restoreId=True) -> bool:
        if hashmap is None:
            hashmap = {}
        try:
            if restoreId:
                self.id = data["id"]
            hashmap[data["id"]] = self

            self.pos = (data["posX"], data["posY"])
            self.title = data["title"]

            data["inputs"].sort(
                key=lambda socket: socket["index"] + socket["position"] * 1000
            )
            data["outputs"].sort(
                key=lambda socket: socket["index"] + socket["position"] * 1000
            )

            numberOfInputs = len(data["inputs"])
            numberOfOutputs = len(data["outputs"])

            self.inputSockets = []
            for socketData in data["inputs"]:
                newSocket = Socket(
                    node=self,
                    index=socketData["index"],
                    location=socketData["position"],
                    socketType=socketData["socketType"],
                    countOnThisNodeSide=numberOfInputs,
                    isInput=True,
                )
                newSocket.deserialize(socketData, hashmap, restoreId)
                self.inputSockets.append(newSocket)

            self.outputSockets = []
            for socketData in data["outputs"]:
                newSocket = Socket(
                    node=self,
                    index=socketData["index"],
                    location=socketData["position"],
                    socketType=socketData["socketType"],
                    countOnThisNodeSide=numberOfOutputs,
                    isInput=False,
                )
                newSocket.deserialize(socketData, hashmap, restoreId)
                self.outputSockets.append(newSocket)
        except Exception as e:
            dumpException(e)

        res = self.content.deserialize(data["content"], hashmap)

        return bool(True & res)
