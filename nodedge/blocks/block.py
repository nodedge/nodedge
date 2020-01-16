import logging

from nodedge.blocks.block_content import BlockContent
from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.node import Node
from nodedge.socket import LEFT_CENTER, RIGHT_CENTER
from nodedge.utils import dumpException


class Block(Node):
    iconPath = ""
    operationTitle = "Undefined"
    operationCode = 0
    contentLabel = ""
    contentLabelObjectName = "blockBackground"

    def __init__(self, scene, inputSocketTypes=(2, 2), outputSocketTypes=(1,)):
        super().__init__(
            scene, self.__class__.operationTitle, inputSocketTypes, outputSocketTypes
        )

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

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

    def checkInputsValidity(self):
        for index in range(len(self.inputSockets)):
            inputNodes = self.inputNodesAt(index)
            inputNodesLength = len(inputNodes)
            if inputNodesLength > 1:
                raise RedundantInputError(
                    f"{inputNodesLength} inputs connected to input socket #{index}."
                )
            if inputNodesLength == 0:
                raise MissInputError(f"No input connected to input socket #{index}.")

    def evalImplementation(self):
        raise NotImplementedError(
            f"evalImplementation has not been overridden by {self.__class__.__name__}"
        )

    def eval(self):
        if not self.isDirty and not self.isInvalid:
            # self.__logger.debug(f"Returning cached value of {self}")
            return self.value

        try:
            self.checkInputsValidity()
            self.value = self.evalImplementation()
            self.isDirty = False
            self.isInvalid = False
            self.graphicsNode.setToolTip("")
            self.markChildrenDirty()
            self.evalChildren()
            return self.value
        except (ValueError, EvaluationError, NotImplementedError) as e:
            self.isInvalid = True
            self.graphicsNode.setToolTip(str(e))
            self.markChildrenDirty()

        except Exception as e:
            self.isInvalid = True
            self.graphicsNode.setToolTip(str(e))
            dumpException(e)
            self.markChildrenDirty()

        # finally:
        #     self.markChildrenDirty()
        #     self.evalChildren()

    def serialize(self):
        res = super().serialize()
        res["operationCode"] = self.__class__.operationCode
        return res

    def deserialize(self, data, hashmap={}, restoreId=True):
        # self.__logger.debug(f"Deserializing block {self.__class__.__name__}")
        res = super().deserialize(data, hashmap, restoreId)
        self.__logger.debug(f"Deserialized block {self.__class__.__name__}: {res}")

        return res


class EvaluationError(Exception):
    pass


class MissInputError(EvaluationError):
    pass


class RedundantInputError(EvaluationError):
    pass
