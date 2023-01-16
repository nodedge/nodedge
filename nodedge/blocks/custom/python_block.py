# -*- coding: utf-8 -*-
from typing import List

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
            BlockParam("input", "", BlockParamType.ShortText),
            BlockParam("output", "", BlockParamType.ShortText),
            BlockParam("intValue", 0, BlockParamType.Int, -5, 6, 5),
            BlockParam("floatValue", 0.0, BlockParamType.Float),
            BlockParam("boolValue", False, BlockParamType.Bool),
        ]

        self.eval()

    # noinspection PyAttributeOutsideInit
    def initInnerClasses(self):
        self.content = GraphicsBlockContent(self)
        self.graphicsNode = GraphicsBlock(self)

    def evalImplementation(self):
        inputValue = self.inputNodeAt(0).eval()
        text = self.params[0].value.replace("\n", "\n    ")

        inputFunction = f"""
def func(inputValue):
    {text}
"""

        print(inputFunction)

        exec(inputFunction, globals())

        self.value = func(inputValue)

        self.isDirty = False
        self.isInvalid = False

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty(True)

        return self.value

    def generateCode(self, currentVarIndex: int, inputVarIndexes: List[int]):
        generatedCode: str = f"var_{str(currentVarIndex)} = {str(self.eval())}\n"
        return generatedCode
