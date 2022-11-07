# -*- coding: utf-8 -*-
"""
Node module containing :class:`~nodedge.node.Node` class.
"""


import logging
from collections import OrderedDict
from typing import Callable, Collection, List, Optional, cast

from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QGraphicsSceneMouseEvent

from nodedge.connector import Socket, SocketLocation
from nodedge.edge import Edge
from nodedge.graphics_node import GraphicsNode
from nodedge.graphics_node_content import GraphicsNodeContent
from nodedge.serializable import Serializable
from nodedge.socket_type import SocketType
# from nodedge.types import Pos
from nodedge.utils import dumpException


class NodesAndSockets:
    """
    :class:`~nodedge.node.NodesAndSockets` class
    """

    def __init__(self, nodes, sockets) -> None:
        """
        :param nodes: list of nodes to add to the structure
        :param sockets: list of sockets to add to the structure
        """
        self.nodes: List["Node"] = nodes
        self.sockets: List["Socket"] = sockets


class Node(Serializable):
    """:class:`~nodedge.node.Node` class representing a node in the `Scene`."""

    GraphicsNodeClass = GraphicsNode
    GraphicsNodeContentClass = GraphicsNodeContent
    SocketClass = Socket
    contentLabelObjectName = "undefined"

    def __init__(
        self,
        scene: "Scene",  # type: ignore
        title: str = "Undefined node",
        inputSocketTypes: Collection[SocketType] = (),
        outputSocketTypes: Collection[SocketType] = (),
    ):
        """
        :param scene: reference to the :class:`~nodedge.scene.Scene`
        :type scene: :class:`~nodedge.scene.Scene`
        :param title: node title shown in scene
        :type title: ``str``
        :param inputSocketTypes: list of types of the input `Sockets`
        :type inputSocketTypes: ``Collection[SocketType]``
        :param outputSocketTypes: list of types of the output `Sockets`
        :type outputSocketTypes: ``Collection[SocketType]``
        """

        super().__init__()
        self._title: str = title
        self.scene: "Scene" = scene  # type: ignore
        self.inputSocketTypes: Collection[SocketType] = inputSocketTypes
        self.outputSocketTypes: Collection[SocketType] = outputSocketTypes

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

        self.selectedListeners: List[Callable] = []

    def __str__(self):
        return (
            f"0x{hex(id(self))[-4:]} {self.__class__.__name__}({self.title}, "
            f"{self.inputSockets}, {self.outputSockets})"
        )

    # noinspection PyAttributeOutsideInit
    def initInnerClasses(self) -> None:
        """
        Set up graphics node and content widget.
        """
        self.content = self.__class__.GraphicsNodeContentClass(self)
        self.graphicsNode = self.__class__.GraphicsNodeClass(self)

    # noinspection PyAttributeOutsideInit
    def initSettings(self) -> None:
        """
        Initialize properties and sockets information.
        """
        self.title: str = self._title
        self._socketSpacing: int = 22
        self._inputSocketPosition: SocketLocation = SocketLocation.LEFT_TOP
        self._outputSocketPosition: SocketLocation = SocketLocation.RIGHT_TOP
        self._inputAllowMultiEdges: bool = False
        self._outputAllowMultiEdges: bool = True
        self.socketOffsets = {
            SocketLocation.LEFT_BOTTOM: -1,
            SocketLocation.LEFT_CENTER: -1,
            SocketLocation.LEFT_TOP: -1,
            SocketLocation.RIGHT_BOTTOM: 1,
            SocketLocation.RIGHT_CENTER: 1,
            SocketLocation.RIGHT_TOP: 1,
        }

    def initSockets(
        self,
        inputs: Collection[SocketType],
        outputs: Collection[SocketType],
        reset: bool = True,
    ) -> None:
        """
        Create input and output sockets.

        :param inputs: list of types of the input `Sockets`. Every type is associated
            with a ``int``
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
            socket = self.__class__.SocketClass(
                node=self,
                index=ind,
                location=self._inputSocketPosition,
                socketType=inp,
                allowMultiEdges=self._inputAllowMultiEdges,
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
                allowMultiEdges=self._outputAllowMultiEdges,
                countOnThisNodeSide=len(outputs),
            )
            self.outputSockets.append(socket)

    def onEdgeConnectionChanged(self, newEdge: Edge) -> None:
        """
        Handle event associated with a change in any of the connections (`Edge`).
        Currently unused.

        :param newEdge: reference to the changed :class:`~nodedge.edge.Edge`
        :type newEdge: :class:`~nodedge.edge.Edge`
        """
        self.__logger.debug(f"{newEdge}")

    def onInputChanged(self, socket: Socket):
        """
        Handle event associated with a change in this node's input edge.
        When it happens, this node and all its descendants are labelled as dirty.

        :param socket: reference to the changed :class:`~nodedge.socket.Socket`
        :type socket: :class:`~nodedge.socket.Socket`
        """

        self.__logger.debug(f"{socket}")
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
    def title(self, newTitle: str) -> None:
        otherNodes = self.scene.nodes.copy()
        if self in self.scene.nodes:
            otherNodes.remove(self)
        alreadyExistingNames = [node.title for node in otherNodes]

        while newTitle in alreadyExistingNames:
            if newTitle[-1].isnumeric():
                newLastCharacter = str(int(newTitle[-1]) + 1)
                newTitle = newTitle[:-1]
                newTitle += newLastCharacter
            else:
                newTitle += "1"

        self._title = newTitle
        self.graphicsNode.title = newTitle

    @property
    def pos(self):
        """
        Retrieve node's position in the scene

        :return: node position
        :rtype: ``QPointF``
        """
        return self.graphicsNode.pos()  # QPointF

    @pos.setter
    def pos(self, pos):
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
        Property stating whether or not this node is marked as `Dirty`, i.e. the node
        has not been evaluated since last node's input/output change.

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
        Property stating whether or not this node is marked as `Invalid`, i.e. the node
        has been evaluated since last node's input/output change,
        but the evaluation was inconsistent.

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
        Retrieve graphics node selection status.
        """
        return self.graphicsNode.isSelected()

    @isSelected.setter
    def isSelected(self, value: bool):
        self.graphicsNode.setSelected(value)
        self.graphicsNode._lastSelectedState = value
        if value is True:
            self.graphicsNode.onSelected()

    def socketPos(self, index: int, location: int, countOnThisSide: int = 1) -> QPointF:
        """
        Get the relative `x, y` position of a :class:`~nodedge.socket.Socket`. This is
        used for placing the :class:`~nodedge.graphics_socket.GraphicsSocket`
        on `Graphics Node`.

        :param index: Order number of the Socket. (0, 1, 2, ...)
        :type index: ``int``
        :param location: `Socket location constant` describing where
            the Socket is located
        :type location: :class:`~nodedge.socket.SocketLocation`
        :param countOnThisSide: Total number of Sockets on this `Socket Position`
        :type countOnThisSide: ``int``
        :return: Position of described Socket on the `Node`
        :rtype: ``QPointF``
        """
        x: int = (
            self.socketOffsets[cast(SocketLocation, location)]
            if (
                location
                in (
                    SocketLocation.LEFT_TOP,
                    SocketLocation.LEFT_CENTER,
                    SocketLocation.LEFT_BOTTOM,
                )
            )
            else self.graphicsNode.width
            + self.socketOffsets[cast(SocketLocation, location)]
        )

        if location in (SocketLocation.LEFT_BOTTOM, SocketLocation.RIGHT_BOTTOM):
            y: float = (
                self.graphicsNode.height
                - self.graphicsNode.edgeRoundness
                - self.graphicsNode.titleVerticalPadding
                - index * self._socketSpacing
            )
        elif location in (SocketLocation.LEFT_CENTER, SocketLocation.RIGHT_CENTER):
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

        elif location in (SocketLocation.LEFT_TOP, SocketLocation.RIGHT_TOP):
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
        # TODO: Investigate why setting graphicsNode to None makes tests crash.
        # self.graphicsNode = None
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
        Mark the children of this node to be `Dirty`. Children are first-level
        descendants. Note: it does not apply to this node.

        :param newValue: ``True`` if children should be `Dirty`,
            ``False`` to un-dirty them.
        :type newValue: ``bool``
        """
        for otherNode in self.getChildNodes():
            otherNode.isDirty = newValue

    def markDescendantsDirty(self, newValue: bool = True) -> None:
        """
        Mark all-level descendants of this `Node` to be `Dirty`.
         Note: it does not apply to this node.

        :param newValue: ``True`` if descendants should be `Dirty`,
            ``False`` to un-dirty them.
        :type newValue: ``bool``
        """
        for otherNode in self.getChildNodes():
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

        :param newValue: ``True`` if children should be `Invalid`, ``False`` to make
            them valid.
        :type newValue: ``bool``
        """
        for otherNode in self.getChildNodes():
            otherNode.isInvalid = newValue

    def markDescendantsInvalid(self, newValue: bool = True) -> None:
        """
        Mark descendants of this node as `Invalid`.
        Note: it does not apply to this node.

        :param newValue: ``True`` if descendants should be `Invalid`,
            ``False`` to make descendants valid.
        :type newValue: ``bool``
        """

        for otherNode in self.getChildNodes():
            otherNode.isInvalid = newValue
            otherNode.markChildrenInvalid(newValue)

    def eval(self, index=0) -> float:
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
        for node in self.getChildNodes():
            # TODO: Investigate if we want to evaluate all the children of the child
            node.eval()

    def getChildNodes(self) -> List["Node"]:
        """
        Retrieve all children connected to this node outputs.

        :return: list of `Nodes` connected to this node from all outputs
        :rtype: List[:class:`~nodedge.node.Node`]
        """
        return self._getRelativeNodes("child")

    def getParentNodes(self) -> List["Node"]:
        """
        Retrieve all parents connected to this node inputs.

        :return: list of `Nodes` connected to this node from all inputs
        :rtype: List[:class:`~nodedge.node.Node`]
        """
        return self._getRelativeNodes("parent")

    def _getRelativeNodes(self, relationship: str) -> List["Node"]:
        """
        Protected method to get relative nodes.

        :param relationship: "child" or "parent"
        :type relationship: str
        :return: relative nodes
        :rtype: List[:class:`~nodedge.node.Node`]
        """
        if relationship == "child":
            socketList: List[Socket] = self.outputSockets
        elif relationship == "parent":
            socketList = self.inputSockets
        else:
            raise NotImplementedError

        if not socketList:
            self.__logger.debug("Socket list is empty")
            return []

        otherNodes: List["Node"] = []
        for socket in socketList:
            for edge in socket.edges:
                otherNode = edge.getOtherSocket(socket).node
                otherNodes.append(otherNode)

        return otherNodes

    def __IONodesAndSocketsAt(self, side: str, index: int) -> NodesAndSockets:
        IONodes = []
        IOSockets = []
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
                if otherSocket is not None:
                    IONodes.append(otherSocket.node)
                    IOSockets.append(otherSocket)
        except IndexError:
            self.__logger.warning(
                f"Trying to get connected {side} node at #{index} "
                f"but {self} has only {len(socketList)} outputs."
            )
        except Exception as e:
            dumpException(e)
        finally:
            nodesAndSockets: NodesAndSockets = NodesAndSockets(IONodes, IOSockets)
            return nodesAndSockets

    def inputNodesAt(self, index: int) -> List["Node"]:
        """
        Get **all** nodes connected to the input specified by `index`.

        :param index: order number of the input socket
        :type index: ``int``
        :return: all :class:`~nodedge.node.Node` instances which are connected
            to the specified input or ``[]`` if there is no connection
            or index is out of range.
        :rtype: List[:class:`~nodedge.node.Node`]
        """
        return self.__IONodesAndSocketsAt("input", index).nodes

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

    def inputNodeAndSocketAt(self, index):
        try:
            return {
                "node": self.__IONodesAndSocketsAt("input", index).nodes[0],
                "socket": self.__IONodesAndSocketsAt("input", index).sockets[0],
            }
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
        :return: all :class:`~nodedge.node.Node` instances which are connected to the
            specified output or ``[]`` if there is no connection or
            index is out of range.
        :rtype: List[:class:`~nodedge.node.Node`]
        """
        return self.__IONodesAndSocketsAt("output", index).nodes

    def serialize(self) -> OrderedDict:
        inputs, outputs = [], []
        for socket in self.inputSockets:
            inputs.append(socket.serialize())
        for socket in self.outputSockets:
            outputs.append(socket.serialize())

        serializedContent: OrderedDict = OrderedDict()
        if isinstance(self.content, Serializable):
            serializedContent = self.content.serialize()
        return OrderedDict(
            [
                ("id", self.id),
                ("title", self.title),
                ("posX", self.graphicsNode.scenePos().x()),
                ("posY", self.graphicsNode.scenePos().y()),
                ("inputSockets", inputs),
                ("outputSockets", outputs),
                ("content", serializedContent),
            ]
        )

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = True,
        *args,
        **kwargs,
    ):
        if hashmap is None:
            hashmap = {}
        try:
            if restoreId:
                self.id = data["id"]
            hashmap[data["id"]] = self

            self.pos = (data["posX"], data["posY"])
            self.title = data["title"]

            data["inputSockets"].sort(key=lambda s: s["index"] + s["location"] * 1000)
            data["outputSockets"].sort(key=lambda s: s["index"] + s["location"] * 1000)

            numberOfInputs = len(data["inputSockets"])
            numberOfOutputs = len(data["outputSockets"])

            # First method: delete existing sockets. When we do this,
            # deserialization will override even the number of sockets defined in the
            # constructor of a node...
            # Second method: reuse existing sockets,
            # dont create new ones if not necessary

            # self.inputSockets = []
            # for socketData in data["inputs"]:
            #     newSocket = Socket(
            #         node=self,
            #         index=socketData["index"],
            #         location=socketData["position"],
            #         socketType=socketData["socketType"],
            #         countOnThisNodeSide=numberOfInputs,
            #         isInput=True,
            #     )
            #     newSocket.deserialize(socketData, hashmap, restoreId)
            #     self.inputSockets.append(newSocket)

            for socketData in data["inputSockets"]:
                found = None
                for socket in self.inputSockets:
                    if socket.index == socketData["index"]:
                        found = socket
                        found.socketType = SocketType(socketData["socketType"])
                        break
                if found is None:
                    self.__logger.debug(
                        "Deserialization of socket data has not found "
                        "input socket with index:",
                        socketData["index"],
                    )
                    self.__logger.debug("Actual socket data:", socketData)

                    # Create new socket for this
                    found = self.__class__.SocketClass(
                        node=self,
                        index=socketData["index"],
                        location=socketData["location"],
                        socketType=SocketType(socketData["socketType"]),
                        countOnThisNodeSide=numberOfInputs,
                        isInput=True,
                    )

                    # Append newly created output to the list
                    self.inputSockets.append(found)

                found.deserialize(socketData, hashmap, restoreId)

            # self.outputSockets = []
            # for socketData in data["outputs"]:
            #     newSocket = Socket(
            #         node=self,
            #         index=socketData["index"],
            #         location=socketData["position"],
            #         socketType=socketData["socketType"],
            #         countOnThisNodeSide=numberOfOutputs,
            #         isInput=False,
            #     )
            #     newSocket.deserialize(socketData, hashmap, restoreId)
            #     self.outputSockets.append(newSocket)

            for socketData in data["outputSockets"]:
                found = None
                for socket in self.outputSockets:
                    # print("\t", socket, socket.index, "=?", socket_data['index'])
                    if socket.index == socketData["index"]:
                        found = socket
                        found.socketType = SocketType(socketData["socketType"])
                        break
                if found is None:
                    self.__logger.debug(
                        "Deserialization of socket data has not found output socket "
                        "with index:",
                        socketData["index"],
                    )
                    # Create new socket for this
                    found = self.__class__.SocketClass(
                        node=self,
                        index=socketData["index"],
                        location=socketData["location"],
                        socketType=SocketType(socketData["socketType"]),
                        countOnThisNodeSide=numberOfOutputs,
                        isInput=False,
                    )
                    # Append newly created output to the list
                    self.outputSockets.append(found)
                found.deserialize(socketData, hashmap, restoreId)

        except Exception as e:
            dumpException(e)

        res = self.content.deserialize(data["content"], hashmap)

        return bool(True & res)

    def onDoubleClicked(self, event: QGraphicsSceneMouseEvent) -> None:
        """
        Callback when the :class:`~nodedge.graphics_node.GraphicsNode`
        is double clicked.

        :param event: Qt double click event
        :type event: ``QMouseEvent``
        """

        self.__logger.debug(f"Graphics node has been double clicked: {event}")

    def getNodeContentClass(self):
        """
        Returns class representing node content.
        """
        return self.__class__.GraphicsNodeContentClass

    def getGraphicsNodeClass(self):
        """
        Returns class representing graphics node.
        """
        return self.__class__.GraphicsNodeClass

    def getSocketScenePosition(self, socket: Socket) -> QPointF:
        """
        Get absolute :class:`~nodedge.socket.Socket` position in the
        :class:`~nodedge.socket.Socket`.

        :param socket: The socket from which we want to get the position
        :type socket: :class:`~nodedge.socket.Socket`
        :return: :class:`~nodedge.socket.Socket`'s scene position
        :rtype: ``QPointF``
        """
        nodePos: QPointF = self.graphicsNode.pos()
        socketPos: QPointF = self.socketPos(
            socket.index, socket.location, socket.countOnThisNodeSide
        )
        return QPointF(nodePos.x() + socketPos.x(), nodePos.y() + socketPos.y())

    def addSelectedListener(self, callback):
        self.selectedListeners.append(callback)

    def onDeserialized(self, data: dict):
        """Event manually called when this node was deserialized.
        Currently called when node is deserialized from :class:`~nodedge.scene.Scene`.

        :param data: data which have been deserialized
        :type data: ``dict``
        """
        pass
