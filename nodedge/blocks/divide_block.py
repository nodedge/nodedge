# -*- coding: utf-8 -*-
from nodedge.blocks.block import Block, EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, OP_NODE_DIVIDE, registerNode


@registerNode(OP_NODE_DIVIDE)
class DivideBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/divide.png"
    operationCode = OP_NODE_DIVIDE
    operationTitle = "Divide"
    contentLabel = "/"
    contentLabelObjectName = "BlockBackground"
    evalString = "truediv"

    def evalImplementation(self):
        i0 = self.inputNodeAt(0)
        i1 = self.inputNodeAt(1)

        try:
            result = i0.eval() / i1.eval()
        except TypeError as e:
            raise EvaluationError(e)
        except ZeroDivisionError:
            raise EvaluationError("Division by 0 is not possible.")

        self.value = result

        return self.value
