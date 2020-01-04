from nodedge.blocks.block import Block
from nodedge.blocks.block_config import registerNode, OP_NODE_DIVIDE, BLOCKS_ICONS_PATH


@registerNode(OP_NODE_DIVIDE)
class DivideBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/divide.png"
    operationCode = OP_NODE_DIVIDE
    operationTitle = "Divide"
    contentLabel = "/"
    contentLabelObjectName = "BlockBackground"
