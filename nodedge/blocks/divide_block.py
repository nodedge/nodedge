from nodedge.blocks.block import *
from nodedge.blocks.block_config import registerNode, OP_NODE_DIVIDE, BLOCKS_ICONS_PATH


@registerNode(OP_NODE_DIVIDE)
class DivideBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/divide.png"
    operationCode = OP_NODE_DIVIDE
    operationTitle = "Divide"
    contentLabel = "/"
    contentLabelObjectName = "BlockBackground"

    def evalImplementation(self):
        i0 = self.inputNodeAt(0)
        i1 = self.inputNodeAt(1)

        try:
            result = i0.eval() / i1.eval()
        except TypeError as e:
            raise EvaluationError(e)
        except ZeroDivisionError as e:
            raise EvaluationError("Division by 0 is not possible.")

        self.value = result

        return self.value
