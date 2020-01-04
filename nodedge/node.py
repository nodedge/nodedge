from nodedge.graphics_node import GraphicsNode
from nodedge.node_content import NodeContent
from nodedge.socket import *
from nodedge.utils import dumpException


class Node(Serializable):
    def __init__(self, scene, title="Undefined node", inputs=[], outputs=[]):
        super().__init__()
        self._title = title
        self.scene = scene

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.initInnerClasses()
        self.initSettings()

        self.scene.addNode(self)
        self.scene.graphicsScene.addItem(self.graphicsNode)

        self.inputs = []
        self.outputs = []
        self.initSockets(inputs, outputs)

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

    def initSockets(self, inputs, outputs, reset=True):
        """"Create sockets for inputs and outputs"""
        # Reset existing sockets.
        if reset:
            if hasattr(self, "inputs") and hasattr(self, "outputs"):
                for socket in self.inputs+self.outputs:
                    self.scene.graphicsScene.removeItem(socket.graphicsSocket)
                self.inputs = []
                self.outputs = []

        # Create new sockets.
        for ind, inp in enumerate(inputs):
            socket = Socket(node=self,
                            index=ind,
                            position=self._inputSocketPosition,
                            socketType=inp,
                            allowsMultiEdges=self._inputAllowsMultiEdges,
                            countOnThisNodeSide=len(inputs),
                            isInput=True)
            self.inputs.append(socket)

        for ind, out in enumerate(outputs):
            socket = Socket(node=self,
                            index=ind,
                            position=self._outputSocketPosition,
                            socketType=out,
                            allowsMultiEdges=self._outputAllowsMultiEdges,
                            countOnThisNodeSide=len(outputs),
                            isInput=False)
            self.outputs.append(socket)

    def __str__(self):
        return f"0x{hex(id(self))[-4:]} Node({self.title}, {self.inputs}, {self.outputs})"

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.graphicsNode.title = value

    @property
    def pos(self):
        return self.graphicsNode.pos() # QPointF
    @pos.setter
    def pos(self, pos):
        try:
            x, y = pos
        except ValueError:
            raise ValueError("Pass an iterable with two numbers.")
        self.graphicsNode.setPos(x, y)

    def socketPos(self, index, position, countOnThisSide=1):
        x = 0 if (position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM)) else self.graphicsNode.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = self.graphicsNode.height - self.graphicsNode.edgeRoundness - self.graphicsNode.titleVerticalPadding \
                - index * self._socketSpacing
        elif position in (LEFT_CENTER, RIGHT_CENTER):
            numberOfSockets = countOnThisSide
            nodeHeight = self.graphicsNode.height
            topOffset = self.graphicsNode.titleHeight + 2 * self.graphicsNode.titleVerticalPadding
            availableHeight = nodeHeight - topOffset

            totalHeightofAllSockets = numberOfSockets * self._socketSpacing

            newTop = availableHeight - totalHeightofAllSockets

            y = topOffset + availableHeight / 2.0 + (index - 0.5) * self._socketSpacing
            if numberOfSockets > 1:
                y -= self._socketSpacing * (numberOfSockets - 1) / 2

        elif position in (LEFT_TOP, RIGHT_TOP):
            y = self.graphicsNode.titleHeight + self.graphicsNode.titleVerticalPadding \
                + self.graphicsNode.edgeRoundness + index * self._socketSpacing
        else:
            y = 0

        return [x, y]

    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            for edge in socket.edges:
                self.__logger.debug("Updating socket edges.")
                edge.updatePos()
            else:
                self.__logger.debug("No edge is connected.")

    def remove(self):
        self.__logger.debug(f"Removing {self}")
        self.__logger.debug("Removing all edges connected to the node.")
        for socket in (self.inputs + self.outputs):
            socket.removeAllEdges()
        self.__logger.debug("Removing the graphical node.")
        self.scene.graphicsScene.removeItem(self.graphicsNode)
        self.graphicsNode = None
        self.__logger.debug("Removing the node from the scene.")
        self.scene.removeNode(self)

    # Node evaluation functions

    @property
    def isDirty(self):
        return self._isDirty
    @isDirty.setter
    def isDirty(self, value):
        if self._isDirty != value:
            self._isDirty = value

        if self._isDirty:
            self.onMarkedDirty()

    def onMarkedDirty(self):
        pass

    def markChildrenDirty(self, newValue=True):
        for otherNode in self.getChildrenNodes():
            otherNode.isDirty = newValue

    def markDescendantsDirty(self, newValue=True):
        for otherNode in self.getChildrenNodes():
            otherNode.isDirty = newValue
            otherNode.markChildrenDirty(newValue)

    @property
    def isInvalid(self):
        return self._isInvalid
    @isInvalid.setter
    def isInvalid(self, value):
        if self._isInvalid != value:
            self._isInvalid = value

        if self._isInvalid:
            self.onMarkedInvalid()

    def onMarkedInvalid(self):
        pass

    def markChildrenInvalid(self, newValue=True):
        for otherNode in self.getChildrenNodes():
            otherNode.isInvalid = newValue

    def markDescendantsInvalid(self, newValue=True):
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

    # Traversing node functions

    def getChildrenNodes(self):
        if not self.outputs:
            return []

        otherNodes = []
        for ix in range(len(self.outputs)):
            for edge in self.outputs[ix].edges:
                otherNode = edge.getOtherSocket(self.outputs[ix]).node
                otherNodes.append(otherNode)

        return otherNodes

    # Serialization functions
    def serialize(self):
        inputs, outputs = [], []
        for socket in self.inputs:
            inputs.append(socket.serialize())
        for socket in self.outputs:
            outputs.append(socket.serialize())

        return OrderedDict([("id",  self.id),
                            ("title", self.title),
                            ("posX", self.graphicsNode.scenePos().x()),
                            ("posY", self.graphicsNode.scenePos().y()),
                            ("inputs", inputs),
                            ("outputs", outputs),
                            ("content", self.content.serialize()),

                            ])

    def deserialize(self, data, hashmap={}, restoreId=True):
        try:
            if restoreId:
                self.id = data["id"]
            hashmap[data["id"]] = self

            self.pos = (data["posX"], data["posY"])
            self.title = data["title"]

            data["inputs"].sort(key=lambda socket: socket["index"]+socket["position"]*1000)
            data["outputs"].sort(key=lambda socket: socket["index"]+socket["position"]*1000)

            numberOfInputs = len(data["inputs"])
            numberOfOutputs = len(data["outputs"])

            self.inputs = []
            for socketData in data["inputs"]:
                newSocket = Socket(node=self, index=socketData["index"], position=socketData["position"],
                                   socketType=socketData["socketType"], countOnThisNodeSide=numberOfInputs, isInput=True)
                newSocket.deserialize(socketData, hashmap, restoreId)
                self.inputs.append(newSocket)

            self.outputs = []
            for socketData in data["outputs"]:
                newSocket = Socket(node=self, index=socketData["index"], position=socketData["position"],
                                   socketType=socketData["socketType"], countOnThisNodeSide=numberOfOutputs, isInput=False)
                newSocket.deserialize(socketData, hashmap, restoreId)
                self.outputs.append(newSocket)
        except Exception as e:
            dumpException(e)

        res = self.content.deserialize(data["content"], hashmap)

        return True & res
