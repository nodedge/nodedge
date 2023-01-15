# -*- coding: utf-8 -*-
from typing import List

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import registerNode
from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.blocks.graphics_input_block_content import GraphicsInputBlockContent
from nodedge.blocks.op_node import OP_NODE_CUSTOM_GAIN
from nodedge.socket_type import SocketType


@registerNode(OP_NODE_CUSTOM_GAIN)
class GainBlock(Block):
    icon = f""
    operationCode = OP_NODE_CUSTOM_GAIN
    operationTitle = "Gain"
    contentLabel = "Gain2"
    contentLabelObjectName = "InputBlockContent"
    library = "maths"
    libraryTitle = "maths"
    inputSocketTypes: List[SocketType] = [SocketType.Number]
    outputSocketTypes: List[SocketType] = [SocketType.Number]

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
        inputValue = self.inputNodeAt(0).eval()
        gain = float(self.content.edit.text())

        self.value = inputValue * gain

        self.isDirty = False
        self.isInvalid = False

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty(True)

        return self.value

    def generateCode(self, currentVarIndex: int, inputVarIndexes: List[int]):
        generatedCode: str = f"var_{str(currentVarIndex)} = {str(self.eval())}\n"
        return generatedCode
