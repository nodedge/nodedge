# -*- coding: utf-8 -*-
from typing import List

from numpy import array

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import registerNode
from nodedge.blocks.block_param import BlockParam, BlockParamType
from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.blocks.graphics_block_content import GraphicsBlockContent
from nodedge.blocks.op_node import OP_NODE_CUSTOM_PYTHON
from nodedge.socket_type import SocketType


@registerNode(OP_NODE_CUSTOM_PYTHON)
class PythonBlock(Block):
    icon = f""
    operationCode = OP_NODE_CUSTOM_PYTHON
    operationTitle = "Python"
    contentLabel = "Python"
    contentLabelObjectName = "BlockContent"
    library = "custom"
    libraryTitle = "custom"
    inputSocketTypes: List[SocketType] = [SocketType.Number]
    outputSocketTypes: List[SocketType] = [SocketType.Number]

    def __init__(self, scene):
        super().__init__(
            scene,
            inputSocketTypes=self.__class__.inputSocketTypes,
            outputSocketTypes=self.__class__.outputSocketTypes,
        )

        self.params = [
            BlockParam("code", "", BlockParamType.LongText),
        ]

        self.eval()

    # noinspection PyAttributeOutsideInit
    def initInnerClasses(self):
        self.content = GraphicsBlockContent(self)
        self.graphicsNode = GraphicsBlock(self)

    def evalImplementation(self):
        inputValue = self.inputNodeAt(0).eval()
        inputNodeTitle = self.inputNodeAt(0).title
        funcTitle = "function_" + self.title.lower()
        text = self.params[0].value.replace("\n", "\n    ")

        inputFunction = f"def {funcTitle}({inputNodeTitle}):\n    {text}"

        exec(inputFunction, globals())

        functionEvaluationStr = f"{funcTitle}({inputValue.__repr__()})"
        self.value = eval(functionEvaluationStr)

        self.isDirty = False
        self.isInvalid = False

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty(True)

        return self.value

    def generateCode(self, currentVarIndex: int, inputVarIndexes: List[int]):
        inputNode = self.inputNodeAt(0)
        if inputNode is None:
            return ""
        inputValue = inputNode.eval()
        inputNodeName = inputNode.title.lower()
        text = self.params[0].value.replace("\n", "\n    ")
        funcTitle = "function_" + self.title

        inputFunction = f"def {funcTitle}({inputNodeName}):\n    {text}"
        generatedCode: str = (
            f"var_{self.title.lower()} = {funcTitle}(var_{inputNodeName})\n"
        )
        return inputFunction + "\n" + generatedCode
