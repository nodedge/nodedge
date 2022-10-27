# -*- coding: utf-8 -*-
import logging
from typing import List

from numpy import deg2rad

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.blocks.block_exception import EvaluationError
from nodedge.connector import SocketType

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.op_node import OP_NODE_NUMPY_DEG2RAD
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_NUMPY_DEG2RAD)
class NumpyDeg2RadBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/deg2rad_100.png"
    operationCode = OP_NODE_NUMPY_DEG2RAD
    operationTitle = "Deg to rad"
    contentLabel = ""
    contentLabelObjectName = "BlockBackground"
    evalString = "deg2rad"
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
            operation = f"{NumpyDeg2RadBlock.evalString}({', '.join(evaluatedInputs)})"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
