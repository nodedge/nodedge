from nodedge.blocks.block import Block
from nodedge.blocks.block_config import registerNode, OP_NODE_ADD, BLOCKS_ICONS_PATH


@registerNode(OP_NODE_ADD)
class AddBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/add.png"
    operationCode = OP_NODE_ADD
    operationTitle = "Add"
    contentLabel = "+"
    contentLabelObjectName = "BlockBackground"