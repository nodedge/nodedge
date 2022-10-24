# -*- coding: utf-8 -*-
from typing import List

import logging
from numpy import exp

from nodedge.blocks.block import Block
from nodedge.blocks.block_exception import EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.connector import SocketType

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.op_node import OP_NODE_NUMPY_EXP
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_NUMPY_EXP)
class NumpyExpBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/exp_100.png"
    operationCode = OP_NODE_NUMPY_EXP
    operationTitle = "Exponential"
    contentLabel = ""
    contentLabelObjectName = "BlockBackground"
    evalString = "exp"
    library = "numpy"
    inputSocketTypes: List[SocketType] = [
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
            operation = f"{NumpyExpBlock.evalString}({', '.join(evaluatedInputs)})"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
