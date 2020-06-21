# -*- coding: utf-8 -*-
from nodedge.blocks.block import Block, EvaluationError
from nodedge.blocks.block_config import (
    BLOCKS_ICONS_PATH,
    OP_NODE_MULTIPLY,
    registerNode,
)


@registerNode(OP_NODE_MULTIPLY)
class MultiplyBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/multiply.png"
    operationCode = OP_NODE_MULTIPLY
    operationTitle = "Multiply"
    contentLabel = "*"
    contentLabelObjectName = "BlockBackground"

    def evalImplementation(self):
        i0 = self.inputNodeAt(0)
        i1 = self.inputNodeAt(1)

        try:
            result = i0.eval() * i1.eval()
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
