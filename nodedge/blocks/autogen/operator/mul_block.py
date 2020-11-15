# -*- coding: utf-8 -*-
import logging
from operator import mul

from nodedge.blocks.block import Block
from nodedge.blocks.block_exception import EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.connector import SocketType

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.block_config import OP_NODE_MULTIPLY
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_MULTIPLY)
class MulBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/multiply_100.png"
    operationCode = OP_NODE_MULTIPLY
    operationTitle = "Multiplication"
    contentLabel = "*"
    contentLabelObjectName = "BlockBackground"
    evalString = "mul"
    library = "operator"
    inputSocketTypes = (SocketType.Number, SocketType.Number,)
    outputSocketTypes = (SocketType.Number,)

    def evalImplementation(self):
        inputs = []
        for i in range(len(self.inputSockets)):
            inputs.append(self.inputNodeAt(i))

        try:
            evaluatedInputs = [str(currentInput.eval()) for currentInput in inputs]
            operation = f"{MulBlock.evalString}({', '.join(evaluatedInputs)})"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
