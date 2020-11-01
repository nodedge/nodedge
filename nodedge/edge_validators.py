# -*- coding: utf-8 -*-
"""Edge validators module containing the Edge Validator functions which can be
registered as callbacks to :class:`~nodedge.edge.Edge` class.

Example of registering Edge Validator callbacks:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can register validation callbacks once for example on the bottom of node_edge.py
file or on the application start with calling this:

.. code-block:: python

    from nodedge.edge_validators import *

    Edge.registerEdgeValidator(edgeValidatorDebug)
    Edge.registerEdgeValidator(edgeCannotConnectTwoOutputsOrTwoInputs)
    Edge.registerEdgeValidator(edgeCannotConnectInputAndOutputOfSameNode)

"""

from nodedge.connector import Socket

DEBUG = False


def printError(*args):
    """Helper method which prints to console if `DEBUG` is set to `True`"""
    if DEBUG:
        print("Edge Validation Error:", *args)


def edgeValidatorDebug(inputSocket: Socket, outputSocket: Socket) -> bool:
    """This will consider edge always valid, however writes bunch of debug stuff into
    console"""
    print("VALIDATING:")
    print(
        inputSocket,
        "input" if inputSocket.isInput else "output",
        "of node",
        inputSocket.node,
    )
    for s in inputSocket.node.inputs + inputSocket.node.outputs:
        print("\t", s, "input" if s.is_input else "output")
    print(
        outputSocket,
        "input" if inputSocket.isInput else "output",
        "of node",
        outputSocket.node,
    )
    for s in outputSocket.node.inputs + outputSocket.node.outputs:
        print("\t", s, "input" if s.isInput else "output")

    return True


def edgeCannotConnectTwoOutputsOrTwoInputs(
    inputSocket: Socket, outputSocket: Socket
) -> bool:
    """Edge is invalid if it connects 2 output sockets or 2 input sockets"""
    if inputSocket.isOutput and outputSocket.isOutput:
        printError("Connecting 2 outputs")
        return False

    if inputSocket.isInput and outputSocket.isInput:
        printError("Connecting 2 inputs")
        return False

    return True


def edgeCannotConnectInputAndOutputOfSameNode(
    inputSocket: Socket, outputSocket: Socket
) -> bool:
    """Edge is invalid if it connects the same node"""
    if inputSocket.node == outputSocket.node:
        printError("Connecting the same node")
        return False

    return True
