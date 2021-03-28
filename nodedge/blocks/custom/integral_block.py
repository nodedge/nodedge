# -*- coding: utf-8 -*-
from typing import List

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import (
    BLOCKS_ICONS_PATH,
    OP_NODE_INTEGRAL,
    registerNode,
)
from nodedge.connector import SocketType


@registerNode(OP_NODE_INTEGRAL)
class InputBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/integral.png"
    operationCode = OP_NODE_INTEGRAL
    operationTitle = "Integral"
    contentLabel = ""
    contentLabelObjectName = "BlockBackground"
    library = "common"
    inputSocketTypes: List[SocketType] = [
        SocketType.Number,
    ]
    outputSocketTypes: List[SocketType] = [
        SocketType.Number,
    ]

    def generateCode(self, currentVarIndex: int, inputVarIndexes: List[int]):
        generatedCode: str = f"var_{str(currentVarIndex)} = {str(self.eval())}\n"
        return generatedCode
