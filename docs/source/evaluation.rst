.. _evaluation:

Evaluation
==========

The evaluation system uses
:func:`~nodedge.node.Node.eval` and
:func:`~nodedge.node.Node.evalChildren`. ``eval`` is supposed to be overridden by your own
implementation. The evaluation logic uses Flags for marking the `Nodes` as `Dirty` and/or `Invalid`.

Evaluation Functions
--------------------

There are 2 main methods used for the evaluation:

- :func:`~nodedge.node.Node.eval`
- :func:`~nodedge.node.Node.evalChildren`

These functions are mutually exclusive. That means that ``evalChildren`` does **not** eval the current `Node`,
but only children of the current `Node`.

By default the implementation of :func:`~nodedge.node.Node.eval` is "empty" and return 0. However, if successful, eval resets the `Node` not to be `Dirty` nor `Invalid`.
This method is supposed to be overridden by your own implementation. If you look for examples, please check
out ``examples/example_calculator`` to get inspiration on how to setup your own
`Node` evaluation.

The evaluation takes advantage of the `Node` flags described below.

:class:`~nodedge.node.Node` Flags
-----------------------------------------

Each :class:`~nodedge.node.Node` has 2 flags:

- ``Dirty``
- ``Invalid``

The `Invalid` flag has always higher priority over `Dirty`. This means that if the `Node` is `Invalid` it
does not matter whether it is `Dirty` or not.

To mark a node as `Dirty` or `Invalid` there are respective methods :func:`~nodedge.node.Node.markDirty`
and :func:`~nodedge.node.Node.markInvalid`. Both methods take `bool` parameter for the new state.
You can mark `Node` dirty by setting the parameter to ``True``. Also you can un-mark the state by passing
``False`` value.

For both flags there are 3 methods available:

- :func:`~nodedge.node.Node.markInvalid` - to mark only the `Node`
- :func:`~nodedge.node.Node.markChildrenInvalid` - to mark only the direct (first level) children of the `Node`
- :func:`~nodedge.node.Node.markDescendantsInvalid` - to mark it self and all descendant children of the `Node`

The same applies to the `Dirty` flag:

- :func:`~nodedge.node.Node.markDirty` - to mark only the `Node`
- :func:`~nodedge.node.Node.markChildrenDirty` - to mark only the direct (first level) children of the `Node`
- :func:`~nodedge.node.Node.markDescendantsDirty` - to mark it self and all descendant children of the `Node`

Descendants or Children are always connected to the Output(s) of the current `Node`.

When a node is marked as `Dirty` or `Invalid` one of the two event methods,
:func:`~nodedge.node.Node.onMarkedInvalid` or
:func:`~nodedge.node.Node.onMarkedDirty`, is called. By default, these methods do nothing.
However, they are implemented for you to override and use them in your own evaluation system.
