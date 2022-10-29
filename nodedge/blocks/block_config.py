# -*- coding: utf-8 -*-
import os
from typing import Dict

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
