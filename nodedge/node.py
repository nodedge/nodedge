from nodedge.graphics_node import GraphicsNode
from nodedge.node_widget import NodeWidget
from nodedge.socket import *


class Node(Serializable):
    def __init__(self, scene, title="Undefined node", inputs=[], outputs=[]):
        super().__init__()

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self._title = title
        self.scene = scene

        self.content = NodeWidget(self)

        self.graphicsNode = GraphicsNode(self)
        self.title = title

        self.scene.addNode(self)
        self.scene.graphicsScene.addItem(self.graphicsNode)

        self._socket_spacing = 22
        self.inputs = []
        self.outputs = []
        self.initInputsOutputs(inputs, outputs)

    def __str__(self):
        return f"0x{hex(id(self))[-4:]} Node({self.title}, {self.inputs}, {self.outputs})"

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.graphicsNode.title = value

    def initInputsOutputs(self, inputs, outputs):
        counter = 0
        for inp in inputs:
            socket = Socket(node=self, index=counter, position=LEFT_TOP, socketType=inp, allowsMultiEdges=False)
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for out in outputs:
            socket = Socket(node=self, index=counter, position=RIGHT_BOTTOM, socketType=out)
            counter += 1
            self.outputs.append(socket)

    def getSocketPos(self, index, position):
        x = 0 if (position in (LEFT_TOP, LEFT_BOTTOM)) else self.graphicsNode.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = self.graphicsNode.height - (2 * self.graphicsNode.edge_size + index * self._socket_spacing)
        else:
            y = self.graphicsNode.titleHeight + 2 * self.graphicsNode.edge_size + index * self._socket_spacing

        return [x, y]

    @property
    def pos(self):
        return self.graphicsNode.pos() # QPointF

    def setPos(self, x, y):
        self.graphicsNode.setPos(x, y)

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
        if restoreId:
            self.id = data["id"]
        hashmap[data["id"]] = self

        self.setPos(data["posX"], data["posY"])

        self.title = data["title"]

        data["inputs"].sort(key=lambda socket: socket["index"]+socket["position"]*1000)
        data["outputs"].sort(key=lambda socket: socket["index"]+socket["position"]*1000)

        self.inputs = []
        for socketData in data["inputs"]:
            newSocket = Socket(node=self, index=socketData["index"], position=socketData["position"],
                               socketType=socketData["socketType"])
            newSocket.deserialize(socketData, hashmap, restoreId)
            self.inputs.append(newSocket)

        self.outputs = []
        for socketData in data["outputs"]:
            newSocket = Socket(node=self, index=socketData["index"], position=socketData["position"],
                               socketType=socketData["socketType"])
            newSocket.deserialize(socketData, hashmap, restoreId)
            self.outputs.append(newSocket)

        return True
