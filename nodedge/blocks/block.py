from nodedge.node import Node
from nodedge.blocks.block_content import BlockContent
from nodedge.blocks.graphics_block import GraphicsBlock


class Block(Node):
    def __init__(self, scene, operationTitle, operationCode,
                 contentLabel="", contentLabelObjectName="blockBackground",
                 inputs=(2, 2), outputs=(1,)):
        self.operationTitle = operationTitle
        self.operationCode = operationCode
        self.contentLabel = contentLabel
        self.contentLabelObjectName = contentLabelObjectName

        super().__init__(scene, operationTitle, inputs, outputs)

    def initInnerClasses(self):
        self.content = BlockContent(self)
        self.graphicsNode = GraphicsBlock(self)
