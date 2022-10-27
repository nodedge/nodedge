# -*- coding: utf-8 -*-
from typing import List

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.blocks.graphics_input_block_content import GraphicsInputBlockContent
from nodedge.blocks.op_node import OP_NODE_CUSTOM_INPUT
from nodedge.socket_type import SocketType


@registerNode(OP_NODE_CUSTOM_INPUT)
class InputBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/input.png"
    operationCode = OP_NODE_CUSTOM_INPUT
    operationTitle = "Input"
    contentLabel = "In"
    contentLabelObjectName = "InputBlockContent"
    library = "input/output"
    inputSocketTypes: List[SocketType] = []
    outputSocketTypes: List[SocketType] = [
        SocketType.Any,
    ]

    def __init__(self, scene):
        super().__init__(
            scene,
            inputSocketTypes=self.__class__.inputSocketTypes,
            outputSocketTypes=self.__class__.outputSocketTypes,
        )

        self.eval()

    # noinspection PyAttributeOutsideInit
    def initInnerClasses(self):
        self.content = GraphicsInputBlockContent(self)
        self.graphicsNode = GraphicsBlock(self)

        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        rawValue = self.content.edit.text()

        convertedValue = float(rawValue)
        self.value = convertedValue

        self.isDirty = False
        self.isInvalid = False

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty(True)

        return self.value

    def generateCode(self, currentVarIndex: int, inputVarIndexes: List[int]):
        generatedCode: str = f"var_{str(currentVarIndex)} = {str(self.eval())}\n"
        return generatedCode
