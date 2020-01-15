from typing import Collection

from PyQt5.QtCore import QPointF

from nodedge.edge import Edge
from nodedge.graphics_node import GraphicsNode
from nodedge.node_content import NodeContent
from nodedge.socket import *
from nodedge.socket import Socket
from nodedge.utils import dumpException


class Node(Serializable):
    def __init__(
        self,
        scene: "Scene",
        title: str = "Undefined node",
        inputSockets: Collection[Socket] = (),
        outputSockets: Collection[Socket] = (),
    ):
        super().__init__()
        self._title = title
        self.scene = scene

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

        self.initInnerClasses()
        self.initSettings()

        self.scene.addNode(self)
        self.scene.graphicsScene.addItem(self.graphicsNode)

        self.inputSockets = []
        self.outputSockets = []
        self.initSockets(inputSockets, outputSockets)

        # Evaluation attributes
        self._isDirty = False
        self._isInvalid = False

    def initInnerClasses(self):
        self.content = NodeContent(self)
        self.graphicsNode = GraphicsNode(self)

    def initSettings(self):
        self.title = self._title
        self._socketSpacing = 22
        self._inputSocketPosition = LEFT_TOP
        self._outputSocketPosition = RIGHT_BOTTOM
        self._inputAllowsMultiEdges = False
        self._outputAllowsMultiEdges = True

    def initSockets(
        self,
        inputs: Collection[Socket],
        outputs: Collection[Socket],
        reset: bool = True,
    ):
        """"Create sockets for inputs and outputs"""
        # Reset existing sockets.
        if reset:
            if hasattr(self, "inputs") and hasattr(self, "outputs"):
                for socket in self.inputSockets + self.outputSockets:
                    self.scene.graphicsScene.removeItem(socket.graphicsSocket)
                self.inputSockets = []
                self.outputSockets = []

        # Create new sockets.
        for ind, inp in enumerate(inputs):
            socket = Socket(
                node=self,
                index=ind,
                position=self._inputSocketPosition,
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
                position=self._outputSocketPosition,
                socketType=out,
                allowsMultiEdges=self._outputAllowsMultiEdges,
                countOnThisNodeSide=len(outputs),
                isInput=False,
            )
            self.outputSockets.append(socket)

    def __str__(self):
        return f"0x{hex(id(self))[-4:]} Node({self.title}, {self.inputSockets}, {self.outputSockets})"

    def onEdgeConnectionChanged(self, newEdge: Edge):

        self.__logger.debug(f"{newEdge}")

    def onInputChanged(self, newEdge: Edge):
        self.__logger.debug(f"{newEdge}")
        self.isDirty = True
        self.markDescendantsDirty()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value: str):
        self._title = value
        self.graphicsNode.title = value

    @property
    def pos(self):
        return self.graphicsNode.pos()  # QPointF

    @pos.setter
    def pos(self, pos: QPointF):
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
        return self._isDirty

    @isDirty.setter
    def isDirty(self, value: bool):
        if self._isDirty != value:
            self._isDirty = value

        if self._isDirty:
            self.onMarkedDirty()

    @property
    def isInvalid(self):
        return self._isInvalid

    @isInvalid.setter
    def isInvalid(self, value: bool):
        if self._isInvalid != value:
            self._isInvalid = value

        if self._isInvalid:
            self.onMarkedInvalid()

    def socketPos(self, index: int, position: int, countOnThisSide: int = 1):
        x = (
            0
            if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM))
            else self.graphicsNode.width
        )

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = (
                self.graphicsNode.height
                - self.graphicsNode.edgeRoundness
                - self.graphicsNode.titleVerticalPadding
                - index * self._socketSpacing
            )
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            numberOfSockets = countOnThisSide
            nodeHeight = self.graphicsNode.height
            topOffset = (
                self.graphicsNode.titleHeight
                + 2 * self.graphicsNode.titleVerticalPadding
            )
            availableHeight = nodeHeight - topOffset

            # TODO: use total height of all sockets
            # totalHeightofAllSockets = numberOfSockets * self._socketSpacing

            # TODO: use newTop in node
            # newTop = availableHeight - totalHeightofAllSockets

            y = topOffset + availableHeight / 2.0 + (index - 0.5) * self._socketSpacing
            if numberOfSockets > 1:
                y -= self._socketSpacing * (numberOfSockets - 1) / 2

        elif position in (LEFT_TOP, RIGHT_TOP):
            y = (
                self.graphicsNode.titleHeight
                + self.graphicsNode.titleVerticalPadding
                + self.graphicsNode.edgeRoundness
                + index * self._socketSpacing
            )
        else:
            y = 0

        return [x, y]

    def updateConnectedEdges(self):
        for socket in self.inputSockets + self.outputSockets:
            for edge in socket.edges:
                self.__logger.debug("Updating socket edges.")
                edge.updatePos()
            else:
                self.__logger.debug("No edge is connected.")

    def remove(self):
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
        pass

    def markChildrenDirty(self, newValue: bool = True):
        for otherNode in self.getChildrenNodes():
            otherNode.isDirty = newValue

    def markDescendantsDirty(self, newValue: bool = True):
        for otherNode in self.getChildrenNodes():
            otherNode.isDirty = newValue
            otherNode.markChildrenDirty(newValue)

    def onMarkedInvalid(self):
        pass

    def markChildrenInvalid(self, newValue: bool = True):
        for otherNode in self.getChildrenNodes():
            otherNode.isInvalid = newValue

    def markDescendantsInvalid(self, newValue: bool = True):
        for otherNode in self.getChildrenNodes():
            otherNode.isInvalid = newValue
            otherNode.markChildrenInvalid(newValue)

    def eval(self):
        self.isDirty = False
        self.isInvalid = False
        return 0

    def evalChildren(self):
        for node in self.getChildrenNodes():
            node.eval()

    def getChildrenNodes(self):
        if not self.outputSockets:
            return []

        otherNodes = []
        for ix in range(len(self.outputSockets)):
            for edge in self.outputSockets[ix].edges:
                otherNode = edge.getOtherSocket(self.outputSockets[ix]).node
                otherNodes.append(otherNode)

        return otherNodes

    def __IONodesAt(self, side: str, index: int):
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

    def inputNodesAt(self, index: int):
        return self.__IONodesAt("input", index)

    def inputNodeAt(self, index: int):
        try:
            return self.inputNodesAt(index)[0]
        except IndexError:
            # Index Error has already been caught in inputNodesAt, do not log it again.
            return None
        except Exception as e:
            dumpException(e)

    def outputNodesAt(self, index: int):
        return self.__IONodesAt("output", index)

    def serialize(self):
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

    def deserialize(self, data, hashmap={}, restoreId=True):
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
                    position=socketData["position"],
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
                    position=socketData["position"],
                    socketType=socketData["socketType"],
                    countOnThisNodeSide=numberOfOutputs,
                    isInput=False,
                )
                newSocket.deserialize(socketData, hashmap, restoreId)
                self.outputSockets.append(newSocket)
        except Exception as e:
            dumpException(e)

        res = self.content.deserialize(data["content"], hashmap)

        return True & res
