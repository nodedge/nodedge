from nodedge.blocks.block import Block
from nodedge.blocks.block_config import registerNode, OP_NODE_MULTIPLY, BLOCKS_ICONS_PATH


@registerNode(OP_NODE_MULTIPLY)
class MultiplyBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/multiply.png"
    operationCode = OP_NODE_MULTIPLY
    operationTitle = "Multiply"
    contentLabel = "*"
    contentLabelObjectName = "BlockBackground"