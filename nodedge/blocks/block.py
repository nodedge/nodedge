# -*- coding: utf-8 -*-
"""Block module containing :class:`~nodedge.block.Block` class. """

import logging
from collections import OrderedDict
from typing import List, Optional

from nodedge.blocks.block_exception import (
    EvaluationError,
    MissInputError,
    RedundantInputError,
)
from nodedge.blocks.block_param import BlockParam
from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.blocks.graphics_block_content import GraphicsBlockContent
from nodedge.connector import Socket, SocketLocation
from nodedge.node import Node
from nodedge.socket_type import SocketType
from nodedge.utils import dumpException

logger = logging.getLogger(__name__)


class Block(Node):
    """
    :class:`~nodedge.block.Block` class

    A block is node which can be evaluated to produce an output.
    """

    iconPath = ""
    operationTitle = "Undefined"
    operationCode = 0
    contentLabel = ""
    contentLabelObjectName = "blockBackground"
    evalString = ""
    library = ""
    libraryTitle = ""
    inputSocketTypes: List[SocketType] = [SocketType.Any, SocketType.Any]
    outputSocketTypes: List[SocketType] = [
        SocketType.Any,
    ]

    GraphicsNodeClass = GraphicsBlock
    GraphicsNodeContentClass = GraphicsBlockContent

    def __init__(self, scene, inputSocketTypes=(0, 2), outputSocketTypes=(1,)):
        super().__init__(
            scene,
            self.__class__.operationTitle,
            self.__class__.inputSocketTypes,
            self.__class__.outputSocketTypes,
        )

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.value = None

        # A fresh block has not been evaluated yet. It means it is dirty.
        self.isDirty = True
        self._state = None
        self.initialState = None

        self.graphicsNode.content.updateIO()

        self.params: List[BlockParam] = []

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state

        if self.initialState is None:
            self.initialState = state

    # noinspection PyAttributeOutsideInit
    def initSettings(self):
        """
        Initialize the location of the input and output sockets.
        """
        super().initSettings()
        self._inputSocketPosition = SocketLocation.LEFT_TOP
        self._outputSocketPosition = SocketLocation.RIGHT_TOP

    def onInputChanged(self, socket: Optional[Socket] = None) -> None:
        """
        Called when the value of an input has changed.

        :param socket: the socket on which the input has changed
        :return: ``None``
        """
        self.__logger.debug(f"New socket: {socket}")
        self.isDirty = True
        if self.scene.realTimeEval:
            self.eval()

    def checkInputsValidity(self):
        for index in range(len(self.inputSockets)):
            inputNodes = self.inputNodesAt(index)
            inputNodesLength = len(inputNodes)
            if inputNodesLength > 1:
                raise RedundantInputError(
                    f"{inputNodesLength} inputs connected to input socket #{index}."
                )
            if inputNodesLength == 0:
                raise MissInputError(f"No input connected to input socket #{index}.")

    def evalImplementation(self):
        raise NotImplementedError(
            f"evalImplementation has not been overridden by {self.__class__.__name__}"
        )

    def eval(self, index=0):
        if not self.isDirty and not self.isInvalid:
            # self.__logger.debug(f"Returning cached value of {self}")
            return self.value

        try:
            self.checkInputsValidity()
            # TODO: Implement evalInputs (to avoid repeating eval in specific blocks implementations)
            # TODO: Implement checkInputsConsistency (to avoid division by 0, ...)
            # self.evalInputs()
            # self.checkInputsConsistency()
            self.value = self.evalImplementation()
            self.isDirty = False
            self.isInvalid = False
            self.graphicsNode.setToolTip("")
            self.markChildrenDirty()
            self.evalChildren()
            return self.value
        except (ValueError, EvaluationError, NotImplementedError) as e:
            self.isInvalid = True
            self.graphicsNode.setToolTip(str(e))
            self.markChildrenDirty()

        except Exception as e:
            self.isInvalid = True
            self.graphicsNode.setToolTip(str(e))
            dumpException(e)
            self.markChildrenDirty()

        # finally:
        #     self.markChildrenDirty()
        #     self.evalChildren()

    def serialize(self) -> OrderedDict:
        res = super().serialize()
        res["operationCode"] = self.__class__.operationCode
        paramsDict = {}
        for p in self.params:
            paramsDict[p.name] = {
                "value": p.value,
                "type": p.paramType,
                "minValue": p.minValue,
                "maxValue": p.maxValue,
                "step": p.step,
            }
        res["params"] = paramsDict
        return res

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = True,
        *args,
        **kwargs,
    ):
        if hashmap is None:
            hashmap = {}
        res = super().deserialize(data, hashmap, restoreId)
        self.__logger.debug(f"Deserialized block {self.__class__.__name__}: {res}")
        if "params" in data:
            for param in self.params:
                if param.name in data["params"]:
                    param.value = data["params"][param.name]["value"]
                    param.minValue = data["params"][param.name]["minValue"]
                    param.maxValue = data["params"][param.name]["maxValue"]
                    param.step = data["params"][param.name]["step"]

        self.graphicsNode.content.updateIO()
        return res

    def generateCode(self, currentVarIndex: int, inputVarIndexes: List[int]):
        for index in range(len(self.inputSockets)):
            inputNodes = self.inputNodesAt(index)
            inputNodesLength = len(inputNodes)
            if inputNodesLength > 1:
                raise RedundantInputError(
                    f"{inputNodesLength} inputs connected to input socket #{index}."
                )
            if inputNodesLength == 0:
                raise MissInputError(f"No input connected to input socket #{index}.")
        generatedCode: str = "var_" + self.title + " = " + str(self.evalString) + "("
        generatedCode += ", ".join(
            [
                f"var_{self.inputNodeAt(index).title}"  # type: ignore
                for index in range(len(self.inputSockets))
            ]
        )
        return generatedCode + ")\n"

    def resetState(self):
        self.isDirty = True
        self.isInvalid = False
        self.graphicsNode.setToolTip("")
        self.markChildrenDirty()
        self.state = self.initialState
        logger.debug(f"Reset state of {self.title}: {self.state}")
