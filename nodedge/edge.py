from nodedge.graphics_edge import *
from nodedge.utils import dumpException

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2


class Edge(Serializable):
    def __init__(self, scene, startSocket=None, endSocket=None, edgeType=EDGE_TYPE_BEZIER):
        super().__init__()

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        # Default initialization
        self._startSocket = None
        self._endSocket = None

        self.scene = scene
        self.startSocket = startSocket
        self.endSocket = endSocket
        self.edgeType = edgeType

        self.scene.addEdge(self)

    def __str__(self):
        return f"0x{hex(id(self))[-4:]} Edge(0x{hex(id(self.startSocket))[-4:]}, " \
               f"0x{hex(id(self.endSocket))[-4:]}, " \
               f"{self.edgeType})"

    @property
    def startSocket(self):
        return self._startSocket

    @startSocket.setter
    def startSocket(self, value):
        #If the edge was assigned to another socket before, remove the edge from the socket.
        if self._startSocket is not None:
            self._startSocket.removeEdge(self)
        # Assign new start socket.
        self._startSocket = value
        # Add edge to the socket class.
        if self.startSocket is not None:
            self.startSocket.addEdge(self)

    @property
    def endSocket(self):
        return self._endSocket

    @endSocket.setter
    def endSocket(self, value):
        #If the edge was assigned to another socket before, remove the edge from the socket.
        if self._endSocket is not None:
            self._endSocket.removeEdge(self)
        # Assign new end socket.
        self._endSocket = value
        # Add edge to the socket class.
        if self.endSocket is not None:
            self.endSocket.addEdge(self)

    @property
    def edgeType(self):
        return self._edgeType

    @edgeType.setter
    def edgeType(self, value):
        if hasattr(self, "graphicsEdge") and self.graphicsEdge is not None:
            self.scene.graphicsScene.removeItem(self.graphicsEdge)

        self._edgeType = value

        if self.edgeType == EDGE_TYPE_DIRECT:
            self.graphicsEdge = GraphicsEdgeDirect(self)
        elif self.edgeType == EDGE_TYPE_BEZIER:
            self.graphicsEdge = GraphicsEdgeBezier(self)
        else:
            self.graphicsEdge = GraphicsEdgeBezier(self)

        self.scene.graphicsScene.addItem(self.graphicsEdge)

        if self.startSocket is not None:
            self.updatePos()

    def updatePos(self):
        startPos = self.startSocket.socketPos()
        startPos[0] += self.startSocket.node.graphicsNode.pos().x()
        startPos[1] += self.startSocket.node.graphicsNode.pos().y()
        self.graphicsEdge.setSource(*startPos)
        # TODO: simplify terminology: end -> destination | start -> source
        if self.endSocket is not None:
            endPos = self.endSocket.socketPos()
            endPos[0] += self.endSocket.node.graphicsNode.pos().x()
            endPos[1] += self.endSocket.node.graphicsNode.pos().y()
            self.graphicsEdge.setDestination(*endPos)
        else:
            self.graphicsEdge.setDestination(*startPos)

        self.__logger.debug(f"Start socket: {self.startSocket}")
        self.__logger.debug(f"End socket: {self.endSocket}")
        self.graphicsEdge.update()

    def getOtherSocket(self, knownSocket):
        return self.startSocket if knownSocket == self.endSocket else self.endSocket

    def removeFromSockets(self):
        # TODO: Is it meaningful?
        self.endSocket = None
        self.startSocket = None

    def remove(self):
        oldSockets = [self.startSocket, self.endSocket]

        self.__logger.debug(f"Removing {self} from all sockets.")
        self.removeFromSockets()

        self.__logger.debug(f"Removing Graphical eddge: {self.graphicsEdge}")
        self.scene.graphicsScene.removeItem(self.graphicsEdge)
        self.graphicsEdge = None

        self.__logger.debug(f"Removing {self}")
        try:
            self.scene.removeEdge(self)
        except ValueError as e:
            self.__logger.debug(e)

        self.__logger.debug("Edge has been deleted.")

        # Notify nodes from old sockets
        try:
            for socket in oldSockets:
                if socket is not None and socket.node is not None:
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.isInput:
                        socket.node.onInputChanged(self)
        except Exception as e:
            dumpException(e)

    def serialize(self):

        return OrderedDict([("id",  self.id),
                            ("edgeType",  self.edgeType),
                            ("startSocket",  self.startSocket.id),
                            ("endSocket",  self.endSocket.id if self.endSocket is not None else None),
                            ])

    def deserialize(self, data, hashmap={}, restoreId=True):
        if restoreId:
            self.id = data["id"]
        self.startSocket = hashmap[data["startSocket"]]
        self.endSocket = hashmap[data["endSocket"]]
        self.edgeType = data["edgeType"]

        return True

