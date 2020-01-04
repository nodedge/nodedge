from nodedge.blocks.block import Block
from nodedge.blocks.block_config import registerNode, OP_NODE_OUTPUT, BLOCKS_ICONS_PATH
from nodedge.blocks.output_block_content import OutputBlockContent
from nodedge.blocks.graphics_block import GraphicsBlock


@registerNode(OP_NODE_OUTPUT)
class OutputBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/output.png"
    operationCode = OP_NODE_OUTPUT
    operationTitle = "Output"
    contentLabel = "Out"
    contentLabelObjectName = "OutputBlockContent"

    def __init__(self, scene, inputs=(2, 2), outputs=(1,)):
        super().__init__(scene, inputs=(1,), outputs=[])

    def initInnerClasses(self):
        self.content = OutputBlockContent(self)
        self.graphicsNode = GraphicsBlock(self)