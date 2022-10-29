# -*- coding: utf-8 -*-
from typing import List

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.blocks.block_exception import EvaluationError
from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.blocks.graphics_output_block_content import GraphicsOutputBlockContent
from nodedge.blocks.op_node import OP_NODE_CUSTOM_OUTPUT
from nodedge.socket_type import SocketType


@registerNode(OP_NODE_CUSTOM_OUTPUT)
class OutputBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/output.png"
    operationCode = OP_NODE_CUSTOM_OUTPUT
    operationTitle = "Output"
    contentLabel = "Out"
    contentLabelObjectName = "OutputBlockContent"
    library = "input/output"
    inputSocketTypes: List[SocketType] = [
        SocketType.Any,
    ]
    outputSocketTypes: List[SocketType] = []

    # noinspection PyAttributeOutsideInit
    def initInnerClasses(self):
        self.content = GraphicsOutputBlockContent(self)
        self.graphicsNode = GraphicsBlock(self)

    def evalImplementation(self):
        inputNode = self.inputNodeAt(0)

        # TODO: Investigate if eval is really wanted here.
        inputResult = inputNode.eval()
        if inputResult is None:
            raise EvaluationError(
                f"The result of the input {inputNode} evaluation is None."
            )

        self.content.label.setText(f"{inputResult:.2f}")

        return 223
