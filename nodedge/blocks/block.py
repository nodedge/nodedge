# -*- coding: utf-8 -*-
"""Block module containing :class:`~nodedge.block.Block` class. """

import logging
from collections import OrderedDict
from typing import Optional

from nodedge.blocks.graphics_block import GraphicsBlock
from nodedge.blocks.graphics_block_content import GraphicsBlockContent
from nodedge.connector import Socket, SocketLocation
from nodedge.node import Node
from nodedge.utils import dumpException


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

    GraphicsNodeClass = GraphicsBlock
    GraphicsNodeContentClass = GraphicsBlockContent

    def __init__(self, scene, inputSocketTypes=(2, 2), outputSocketTypes=(1,)):
        super().__init__(
            scene, self.__class__.operationTitle, inputSocketTypes, outputSocketTypes
        )

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.value = None

        # A fresh block has not been evaluated yet. It means it is dirty.
        self.isDirty = True

        self.graphicsNode.content.updateIO()

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
        self.__logger.debug(f"New edge: {socket}")
        self.isDirty = True
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

        self.graphicsNode.content.updateIO()
        return res


class EvaluationError(Exception):
    """
    :class:`~nodedge.block.EvaluationError` class

    If a not cannot be evaluated, raise this error.
    """

    pass


class MissInputError(EvaluationError):
    """
    :class:`~nodedge.block.MissInputError` class

    If an input is missing to a block, preventing it to be evaluated, raise this error.
    """

    pass


class RedundantInputError(EvaluationError):
    """
    :class:`~nodedge.block.RedundantInputError` class

    If two different inputs are connected to a single input socket of a block,
    raise this error.
    """

    pass
