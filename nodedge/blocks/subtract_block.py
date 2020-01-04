from nodedge.blocks.block import Block
from nodedge.blocks.block_config import registerNode, OP_NODE_SUBTRACT, BLOCKS_ICONS_PATH


@registerNode(OP_NODE_SUBTRACT)
class SubtractBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/subtract.png"
    operationCode = OP_NODE_SUBTRACT
    operationTitle = "Subtract"
    contentLabel = "-"
    contentLabelObjectName = "BlockBackground"