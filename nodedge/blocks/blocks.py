import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from nodedge.utils import dumpException
from nodedge.blocks.block_config import *
from nodedge.blocks.block import Block
from nodedge.node_content import NodeContent
from nodedge.blocks.graphics_block import GraphicsBlock

BLOCKS_ICONS_PATH = f"{os.path.dirname(__file__)}/../resources/node_icons"


@registerNode(OP_NODE_INPUT)
class InputBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/input.png"
    operationCode = OP_NODE_INPUT
    operationTitle = "Input"
    contentLabel = "In"
    contentLabelObjectName = "InputBlockContent"

    def __init__(self, scene, inputs=(2, 2), outputs=(1,)):
        super().__init__(scene, inputs=[], outputs=(1,))

    def initInnerClasses(self):
        self.content = InputBlockContent(self)
        self.graphicsNode = GraphicsBlock(self)


class InputBlockContent(NodeContent):
    def initUI(self):
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setObjectName(self.node.contentLabelObjectName)

    def serialize(self):
        res = super().serialize()
        res["value"] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}, restoreId=False):
        res = super().deserialize(data, hashmap, restoreId)
        try:
            value = data.value["value"]
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)

        return res

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


class OutputBlockContent(NodeContent):
    def initUI(self):
        self.label = QLabel("42", self)
        self.label.setAlignment(Qt.AlignLeft)
        self.label.setObjectName(self.node.contentLabelObjectName)


@registerNode(OP_NODE_ADD)
class AddBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/add.png"
    operationCode = OP_NODE_ADD
    operationTitle = "Add"
    contentLabel = "+"
    contentLabelObjectName = "BlockBackground"


@registerNode(OP_NODE_SUBTRACT)
class SubtractBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/subtract.png"
    operationCode = OP_NODE_SUBTRACT
    operationTitle = "Subtract"
    contentLabel = "-"
    contentLabelObjectName = "BlockBackground"


@registerNode(OP_NODE_MULTIPLY)
class MultiplyBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/multiply.png"
    operationCode = OP_NODE_MULTIPLY
    operationTitle = "Multiply"
    contentLabel = "*"
    contentLabelObjectName = "BlockBackground"


@registerNode(OP_NODE_DIVIDE)
class DivideBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/divide.png"
    operationCode = OP_NODE_DIVIDE
    operationTitle = "Divide"
    contentLabel = "/"
    contentLabelObjectName = "BlockBackground"


# Way to register by function call
# associateOperationCodeWithBlock(OP_NODE_ADD, AddBlock)
