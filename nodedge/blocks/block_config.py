# -*- coding: utf-8 -*-
import os
from typing import Dict

OP_NODE_INPUT = 1
OP_NODE_OUTPUT = 2
OP_NODE_ADD = 3
OP_NODE_SUBTRACT = 4
OP_NODE_MULTIPLY = 5
OP_NODE_DIVIDE = 6
OP_NODE_MODULO = 7
OP_NODE_POWER = 8
OP_NODE_LESS = 9
OP_NODE_LESS_EQUAL = 10
OP_NODE_EQUAL = 11
OP_NODE_GREATER = 12
OP_NODE_GREATER_EQUAL = 13

# BlockType = TypeVar("BlockType", bound=Block)
BLOCKS: Dict[int, type] = {}

BLOCKS_ICONS_PATH = f"{os.path.dirname(__file__)}/../resources/node_icons"


# Way to register by function call
# associateOperationCodeWithBlock(OP_NODE_ADD, AdditionBlock)


class BlockConfigException(Exception):
    pass


class InvalidNodeRegistration(BlockConfigException):
    pass


class OperationCodeNotRegistered(BlockConfigException):
    pass


def associateOperationCodeWithBlock(operationCode, referenceClass):
    if operationCode in BLOCKS:
        raise InvalidNodeRegistration(
            f"Duplicite node registration of {operationCode}. "
            f"{BLOCKS[operationCode]} already registered."
        )
    BLOCKS[operationCode] = referenceClass


def registerNode(operationCode):
    def decorator(blockClass):
        associateOperationCodeWithBlock(operationCode, blockClass)
        return blockClass

    return decorator


def getClassFromOperationCode(operationCode):
    if operationCode not in BLOCKS:
        raise OperationCodeNotRegistered(f"{operationCode} is not registered yet.")
    return BLOCKS[operationCode]


# Register blocks
# from nodedge.blocks import *

#
# def print_classes():
#     is_class_member = lambda member: inspect.isclass(member) and member.__module__ == __name__
#     clsmembers = inspect.getmembers(sys.modules[__name__], is_class_member)
#
#
# if __name__ == "__main__":
#     import sys, inspect
#
#     print_classes()
#
#
