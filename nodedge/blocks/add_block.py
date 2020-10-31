# -*- coding: utf-8 -*-
import logging
from operator import add

from nodedge.blocks.block import Block, EvaluationError
from nodedge.blocks.block_config import BLOCKS_ICONS_PATH, OP_NODE_ADD, registerNode


@registerNode(OP_NODE_ADD)
class AddBlock(Block):
    icon = f"{BLOCKS_ICONS_PATH}/add.png"
    operationCode = OP_NODE_ADD
    operationTitle = "Add"
    contentLabel = "+"
    contentLabelObjectName = "BlockBackground"
    evalString = "add"

    def evalImplementation(self):
        inputs = []
        for i in range(len(self.inputSockets)):
            inputs.append(self.inputNodeAt(i))

        try:
            operation = f"{AddBlock.evalString}("
            for curr_input in inputs:
                operation += f"{curr_input.eval()},"
            operation = operation[:-1] + ")"
            result = eval(operation)
        except TypeError as e:
            raise EvaluationError(e)

        self.value = result

        return self.value


# TODO: use join method instead ','.join(list_of_strings)
# TODO: Find a way to extract exceptions from evalImplementation
# TODO: Create a script to generate tests for blocks: list of Inputs and list of expected Outputs
