# -*- coding: utf-8 -*-
"""
element.py module containing :class:`~nodedge.element.Element` class.
"""
from collections import OrderedDict
from typing import Optional

from PySide6.QtCore import QPointF

from nodedge.elements.graphics_element import GraphicsElement
from nodedge.serializable import Serializable
from nodedge.types import Pos
from nodedge.utils import dumpException


class Element(Serializable):
    GraphicsElementClass = GraphicsElement

    def __init__(self, scene: "Scene"):  # type: ignore
        super().__init__()

        self.scene: "Scene" = scene  # type: ignore

        self.initInnerClasses()

        self.scene.elements.append(self)
        self.scene.graphicsScene.addItem(self.graphicsElement)

    def initInnerClasses(self):

        self.graphicsElement = self.__class__.GraphicsElementClass(self)

    def serialize(self) -> OrderedDict:
        if isinstance(self.content, Serializable):
            self.content.serialize()

        return OrderedDict(
            [
                ("id", self.id),
                ("posX", self.graphicsElement.scenePos().x()),
                ("posY", self.graphicsElement.scenePos().y()),
            ]
        )

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = True,
        *args,
        **kwargs
    ) -> bool:

        if hashmap is None:
            hashmap = {}
        try:
            if restoreId:
                self.id = data["id"]
            hashmap[data["id"]] = self

            self.pos = (data["posX"], data["posY"])

        except Exception as e:
            dumpException(e)
            return False

        return True

    @property
    def pos(self):
        """
        Retrieve node's position in the scene

        :return: node position
        :rtype: ``QPointF``
        """
        return self.graphicsElement.pos()  # QPointF

    @pos.setter
    def pos(self, pos: Pos):
        if isinstance(pos, (list, tuple)):
            try:
                x, y = pos
                self.graphicsElement.setPos(x, y)

            except ValueError:
                raise ValueError("Pass an iterable with two numbers.")
            except TypeError:
                raise TypeError("Pass an iterable with two numbers.")
        elif isinstance(pos, QPointF):
            self.graphicsElement.setPos(pos)
