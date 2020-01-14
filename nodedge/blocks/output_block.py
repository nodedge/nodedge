from nodedge.blocks.block import Block, EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, OP_NODE_OUTPUT, registerNode
from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.blocks.output_block_content import OutputBlockContent


@registerNode(OP_NODE_OUTPUT)
class OutputBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/output.png"
    operationCode = OP_NODE_OUTPUT
    operationTitle = "Output"
    contentLabel = "Out"
    contentLabelObjectName = "OutputBlockContent"

    def __init__(self, scene, inputSockets=(2, 2), outputSockets=(1,)):
        super().__init__(scene, inputSockets=(1,), outputSockets=[])

    def initInnerClasses(self):
        self.content = OutputBlockContent(self)
        self.graphicsNode = GraphicsBlock(self)

    def evalImplementation(self):
        inputNode = self.inputNodeAt(0)

        # TODO: Investigate if eval is really wanted here.
        inputResult = inputNode.eval()
        if inputResult is None:
            raise EvaluationError(
                f"The result of the input {inputNode} evaluation is None."
            )

        self.content.label.setText(f"{inputResult}")

        return 223
