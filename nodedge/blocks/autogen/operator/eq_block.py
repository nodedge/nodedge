# -*- coding: utf-8 -*-

from nodedge.blocks.block import Block, EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode

try:
    from nodedge.blocks.block_config import OP_NODE_EQUAL
except:
    op_block_string = -1


@registerNode(OP_NODE_EQUAL)
class EqBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/eq.png"
    operationCode = OP_NODE_EQUAL
    operationTitle = "Equal"
    contentLabel = "=="
    contentLabelObjectName = "BlockBackground"
    evalString = "eq"
    library = "operator"

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
