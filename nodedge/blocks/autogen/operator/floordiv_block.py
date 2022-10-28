# -*- coding: utf-8 -*-
import logging
from operator import floordiv
from typing import List

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.blocks.block_exception import EvaluationError
from nodedge.connector import SocketType

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.op_node import OP_NODE_OPERATOR_FLOOR_DIVIDE
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_OPERATOR_FLOOR_DIVIDE)
class FloorDivBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/floor_100.png"
    operationCode = OP_NODE_OPERATOR_FLOOR_DIVIDE
    operationTitle = "Floor division"
    contentLabel = "//"
    contentLabelObjectName = "BlockBackground"
    evalString = "floordiv"
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
            operation = f"{FloorDivBlock.evalString}({', '.join(evaluatedInputs)})"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value