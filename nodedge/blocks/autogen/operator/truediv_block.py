# -*- coding: utf-8 -*-
import logging
from operator import truediv

from nodedge.blocks.block import Block
from nodedge.blocks.block_exception import EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.block_config import OP_NODE_DIVIDE
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_DIVIDE)
class TrueDivBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/divide_100.png"
    operationCode = OP_NODE_DIVIDE
    operationTitle = "Division"
    contentLabel = "/"
    contentLabelObjectName = "BlockBackground"
    evalString = "truediv"
    library = "operator"

    def evalImplementation(self):
        inputs = []
        for i in range(len(self.inputSockets)):
            inputs.append(self.inputNodeAt(i))

        try:
            evaluatedInputs = [str(currentInput.eval()) for currentInput in inputs]
            operation = f"{TrueDivBlock.evalString}({', '.join(evaluatedInputs)})"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value
