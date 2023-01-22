# -*- coding: utf-8 -*-
import logging
from typing import List

from scipy.integrate import quad

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.blocks.block_exception import EvaluationError
from nodedge.socket_type import SocketType

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.op_node import OP_NODE_CUSTOM_INTEGRAL
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_CUSTOM_INTEGRAL)
class IntegralBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/input.png"
    operationCode = OP_NODE_CUSTOM_INTEGRAL
    operationTitle = "Integral"
    contentLabel = ""
    contentLabelObjectName = "IntegralBlockContent"
    library = "integration/derivation"
    libraryTitle = "integration/derivation"
    inputSocketTypes: List[SocketType] = [
        SocketType.Number,
    ]
    outputSocketTypes: List[SocketType] = [
        SocketType.Number,
    ]

    def __init__(self, scene: "Scene"):  # type: ignore
        super().__init__(
            scene,
            inputSocketTypes=self.__class__.inputSocketTypes,
            outputSocketTypes=self.__class__.outputSocketTypes,
        )

        scene: "Scene" = self.scene  # type: ignore

        self.state = [0, 0]
        self.dt = scene.simulator.config.timeStep
        # self.dt = 0.1

        self.eval()

    def evalImplementation(self):
        my_input = self.inputNodeAt(0).eval()

        def my_func(x):
            return my_input

        try:
            self.dt = self.scene.simulator.config.timeStep
            t0 = 0
            t = t0 + self.dt

            # Integrated signal
            result = quad(my_func, t0, t)
            self.state = [self.state[0] + result[0], result[1]]

        except TypeError as e:
            raise EvaluationError(e)

        self.value = self.state[0]

        return self.value
