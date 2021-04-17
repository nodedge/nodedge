# -*- coding: utf-8 -*-
from typing import List

import logging
from operator import eq

from nodedge.blocks.block import Block
from nodedge.blocks.block_exception import EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.connector import SocketType

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.block_config import OP_NODE_EQUAL
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_EQUAL)
class EqBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/equal_sign_100.png"
    operationCode = OP_NODE_EQUAL
    operationTitle = "Equal"
    contentLabel = "=="
    contentLabelObjectName = "BlockBackground"
    evalString = "eq"
    library = "operator"
    inputSocketTypes: List[SocketType] = [
        SocketType.Number,
        SocketType.Number,
    ]
    outputSocketTypes: List[SocketType] = [
        SocketType.Number,
    ]

    def evalImplementation(self):
        inputs = []
        for i in range(len(self.inputSockets)):
            inputs.append(self.inputNodeAt(i))

        try:
            evaluatedInputs = [str(currentInput.eval()) for currentInput in inputs]
            operation = f"{EqBlock.evalString}({', '.join(evaluatedInputs)})"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
