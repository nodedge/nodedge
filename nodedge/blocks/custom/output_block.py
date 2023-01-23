# -*- coding: utf-8 -*-
from typing import List, Optional

import numpy as np

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.blocks.block_exception import EvaluationError
from nodedge.blocks.block_param import BlockParam, BlockParamType
from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.blocks.graphics_output_block_content import GraphicsOutputBlockContent
from nodedge.blocks.op_node import OP_NODE_CUSTOM_OUTPUT
from nodedge.socket_type import SocketType

np.set_printoptions(precision=2)


@registerNode(OP_NODE_CUSTOM_OUTPUT)
class OutputBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/output.png"
    operationCode = OP_NODE_CUSTOM_OUTPUT
    operationTitle = "Output"
    contentLabel = "Out"
    contentLabelObjectName = "OutputBlockContent"
    library = "input/output"
    libraryTitle = "input/output"
    inputSocketTypes: List[SocketType] = [
        SocketType.Any,
    ]
    outputSocketTypes: List[SocketType] = []

    def __init__(self, scene: "Scene"):  # type: ignore
        super().__init__(
            scene,
            inputSocketTypes=self.__class__.inputSocketTypes,
            outputSocketTypes=self.__class__.outputSocketTypes,
        )
        self.state = ""

        self.params = [
            BlockParam("Scientific notation", True, BlockParamType.Bool),
            BlockParam("Digits", 2, BlockParamType.Int),
        ]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

        if self.initialState is None:
            self.initialState = value

        self.content.label.setText(f"{self.state}")

    # noinspection PyAttributeOutsideInit
    def initInnerClasses(self):
        self.content = GraphicsOutputBlockContent(self)
        self.graphicsNode = GraphicsBlock(self)

    def evalImplementation(self):
        inputNode = self.inputNodeAt(0)

        # TODO: Investigate if eval is really wanted here.
        inputResult = inputNode.eval()
        if inputResult is None:
            raise EvaluationError(
                f"The result of the input {inputNode} evaluation is None."
            )

        # TODO: Update label if a parameter has changed.
        digits = self.params[1].value
        if self.params[0].value:
            self.content.label.setText(f"{inputResult:.{digits}E}")
        else:
            self.content.label.setText(f"{inputResult:.{digits}f}")

        return True

    def generateCode(
        self, currentVarIndex: int = 0, inputVarIndexes: Optional[List[int]] = None
    ):
        inputNode = self.inputNodeAt(0)
        if inputNode is not None:
            return f"var_{inputNode.title}"
        else:
            return ""
