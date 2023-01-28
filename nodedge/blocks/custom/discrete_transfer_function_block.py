# -*- coding: utf-8 -*-
import logging
from typing import List

import numpy as np
from scipy import signal
from scipy.signal import dlsim

from nodedge.blocks.block import Block
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, registerNode
from nodedge.blocks.block_exception import EvaluationError
from nodedge.blocks.block_param import BlockParam, BlockParamType
from nodedge.socket_type import SocketType

_LOG = logging.getLogger(__name__)

try:
    from nodedge.blocks.op_node import (
        OP_NODE_CUSTOM_DISCRETE_TRANSFER_FUNCTION,
        OP_NODE_CUSTOM_INTEGRAL,
    )
except NameError:
    _LOG.warning(f"Not registered block: {__name__}")
    op_block_string = -1


@registerNode(OP_NODE_CUSTOM_DISCRETE_TRANSFER_FUNCTION)
class DiscreteTransferFunctionBlock(Block):
    icon = f""
    operationCode = OP_NODE_CUSTOM_DISCRETE_TRANSFER_FUNCTION
    operationTitle = "dtf"
    contentLabel = "dtf"
    contentLabelObjectName = "DiscreteTransferFunctionBlockContent"
    library = "scipy"
    libraryTitle = "advanced_maths"
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

        self.state = None
        self.dt = scene.simulator.config.timeStep
        # self.dt = 0.1

        self.params = [
            BlockParam("numerator", "", BlockParamType.ShortText),
            BlockParam("denominator", "", BlockParamType.ShortText),
            BlockParam("initial state", 0.0, BlockParamType.Float),
        ]

        self.eval()

    def evalImplementation(self):
        my_input = self.inputNodeAt(0).eval()

        try:
            self.dt = self.scene.simulator.config.timeStep
            t0 = 0
            t = t0 + self.dt

            # Integrated signal

            num = eval("np.array(" + self.params[0].value + ")")
            den = eval("np.array(" + self.params[1].value + ")")

            sys = signal.dlti(num, den, dt=self.dt)
            sys = sys._as_ss()
            if self.state is None:
                _, y, state = dlsim(sys, [my_input, 1e6], t=None)
            else:
                _, y, state = dlsim(sys, [my_input, 1e6], t=None, x0=self.state)

            self.state = state[1]

        except TypeError as e:
            raise EvaluationError(e)

        self.value = y[0][0]

        return self.value
