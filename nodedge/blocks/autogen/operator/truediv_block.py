# -*- coding: utf-8 -*-

from nodedge.blocks.block import Block, EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode

try:
    from nodedge.blocks.block_config import OP_NODE_DIVIDE
except:
    op_block_string = -1


@registerNode(OP_NODE_DIVIDE)
class TrueDivBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/truediv.png"
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
