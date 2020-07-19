# -*- coding: utf-8 -*-
"""
Code generator module containing :class:`~nodedge.code_generator.CodeGenerator` class.
"""


class CodeGenerator:
    """
    :class:`~nodedge.code_generator.CodeGenerator` class .
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, scene: "Scene") -> None:  # type: ignore
        self.scene = scene

    def generateCode(self):
        for node in self.scene.nodes:
            node.code()


# TODO: Find a way to generate beautiful code
# TODO: Find inputs blocks, assign them to a variable,
