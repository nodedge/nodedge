# -*- coding: utf-8 -*-
"""Block exception module containing :class:`~nodedge.block_exception.EvaluationError`,
:class:`~nodedge.block_exception.MissInputError`, and :class:`~nodedge.block_exception.RedundantInputError` classes. """


class EvaluationError(Exception):
    """
    :class:`~nodedge.block.EvaluationError` class

    If a block cannot be evaluated, raise this error.
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
