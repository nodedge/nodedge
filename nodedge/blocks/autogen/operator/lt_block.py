# -*- coding: utf-8 -*-
import logging
from operator import lt

from nodedge.blocks.block import Block, EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.block_config import OP_NODE_LESS
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_LESS)
class LtBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/lt.png"
    operationCode = OP_NODE_LESS
    operationTitle = "Less"
    contentLabel = "<"
    contentLabelObjectName = "BlockBackground"
    evalString = "lt"
    library = "operator"

    def evalImplementation(self):
        inputs = []
        for i in range(len(self.inputSockets)):
            inputs.append(self.inputNodeAt(i))

        try:
            evaluatedInputs = [str(currentInput.eval()) for currentInput in inputs]
            operation = f"{LtBlock.evalString}({', '.join(evaluatedInputs)})"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
