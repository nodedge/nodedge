import logging

from nodedge.node import Node
from nodedge.blocks.block_content import BlockContent
from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.socket import LEFT_CENTER, RIGHT_CENTER
from nodedge.utils import dumpException


class Block(Node):
    iconPath = ""
    operationTitle = "Undefined"
    operationCode = 0
    contentLabel = ""
    contentLabelObjectName = "blockBackground"

    def __init__(self, scene, inputs=(2, 2), outputs=(1,)):
        super().__init__(scene, self.__class__.operationTitle, inputs, outputs)

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

        self.value = None

        # A fresh block has not been evaluated yet. It means it is dirty.
        self.isDirty = True

    def initInnerClasses(self):
        self.content = BlockContent(self)
        self.graphicsNode = GraphicsBlock(self)

    def initSettings(self):
        super().initSettings()
        self._inputSocketPosition = LEFT_CENTER
        self._outputSocketPosition = RIGHT_CENTER

    def onInputChanged(self, newEdge):
        self.__logger.debug(f"New edge: {newEdge}")
        self.isDirty = True
        self.eval()

    def evalImplementation(self):
        return 123

    def eval(self):
        if not self.isDirty and not self.isInvalid:
            self.__logger.debug("Returning cached value")
            return self.value

        try:
            val = self.evalImplementation()
            self.isDirty = False
            self.isInvalid = False
            return val
        except Exception as e:
            self.isInvalid = True
            dumpException(e)

    def serialize(self):
        res = super().serialize()
        res["operationCode"] = self.__class__.operationCode
        return res

    def deserialize(self, data, hashmap={}, restoreId=True):
        # self.__logger.debug(f"Deserializing block {self.__class__.__name__}")
        res = super().deserialize(data, hashmap, restoreId)
        self.__logger.debug(f"Deserialized block {self.__class__.__name__}: {res}")

        return res
