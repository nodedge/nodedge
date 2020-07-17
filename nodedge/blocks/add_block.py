# -*- coding: utf-8 -*-

from operator import add

from nodedge.blocks.block import Block, EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, OP_NODE_ADD, registerNode


@registerNode(OP_NODE_ADD)
class AddBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/add.png"
    operationCode = OP_NODE_ADD
    operationTitle = "Add"
    contentLabel = "+"
    contentLabelObjectName = "BlockBackground"
    evalString = "add"

    def evalImplementation(self):
        i0 = self.inputNodeAt(0)
        i1 = self.inputNodeAt(1)

        try:
            operation = f"{AddBlock.evalString}({i0.eval()}, {i1.eval()})"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
