# -*- coding: utf-8 -*-
import logging
from typing import List

from numpy import array, greater_equal

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.blocks.block_exception import EvaluationError
from nodedge.connector import SocketType

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.op_node import OP_NODE_NUMPY_GREATER_EQUAL
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_NUMPY_GREATER_EQUAL)
class NumpyGreaterEqualBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/more_or_equal_100.png"
    operationCode = OP_NODE_NUMPY_GREATER_EQUAL
    operationTitle = "Greater or equal"
    contentLabel = ">="
    contentLabelObjectName = "BlockBackground"
    evalString = "greater_equal"
    library = "numpy"
    libraryTitle = "logics"
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
            evaluatedInputs = [
                currentInput.eval().__repr__() for currentInput in inputs
            ]
            operation = (
                f"{NumpyGreaterEqualBlock.evalString}({', '.join(evaluatedInputs)})"
            )
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
