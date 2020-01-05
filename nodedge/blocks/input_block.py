from nodedge.blocks.block import Block
from nodedge.blocks.block_config import registerNode, OP_NODE_INPUT, BLOCKS_ICONS_PATH
from nodedge.blocks.input_block_content import InputBlockContent
from nodedge.blocks.graphics_block import GraphicsBlock


@registerNode(OP_NODE_INPUT)
class InputBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/input.png"
    operationCode = OP_NODE_INPUT
    operationTitle = "Input"
    contentLabel = "In"
    contentLabelObjectName = "InputBlockContent"

    def __init__(self, scene, inputSockets=(2, 2), outputSockets=(1,)):
        super().__init__(scene, inputSockets=[], outputSockets=(1,))

        self.eval()

    def initInnerClasses(self):
        self.content = InputBlockContent(self)
        self.graphicsNode = GraphicsBlock(self)

        self.content.edit.textChanged.connect(self.onInputChanged)

    def evalImplementation(self):
        rawValue = self.content.edit.text()

        convertedValue = float(rawValue)
        self.value = convertedValue

        self.isDirty = False
        self.isInvalid = False

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty(True)

        return self.value