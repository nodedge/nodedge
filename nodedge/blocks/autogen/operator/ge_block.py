# -*- coding: utf-8 -*-
import logging
from operator import ge

from nodedge.blocks.block import Block
from nodedge.blocks.block_exception import EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.block_config import OP_NODE_GREATER_EQUAL
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_GREATER_EQUAL)
class GeBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/more_or_equal_100.png"
    operationCode = OP_NODE_GREATER_EQUAL
    operationTitle = "Greater or Equal"
    contentLabel = ">="
    contentLabelObjectName = "BlockBackground"
    evalString = "ge"
    library = "operator"

    def evalImplementation(self):
        inputs = []
        for i in range(len(self.inputSockets)):
            inputs.append(self.inputNodeAt(i))

        try:
            evaluatedInputs = [str(currentInput.eval()) for currentInput in inputs]
            operation = f"{GeBlock.evalString}({', '.join(evaluatedInputs)})"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
