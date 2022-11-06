# -*- coding: utf-8 -*-
"""
comment_element.py module containing :class:`~nodedge.comment_element.CommentElement` class.
"""
from nodedge.elements.element import Element
from nodedge.graphics_text_item import GraphicsTextItem


class CommentElement(Element):
    GraphicsElementClass = GraphicsTextItem  # type: ignore

    def __init__(self, scene: "Scene"):  # type: ignore
        super().__init__(scene)

    # noinspection PyAttributeOutsideInit
    def initInnerClasses(self):
        self.content = "Add your text here"
        self.graphicsElement = self.__class__.GraphicsElementClass(self, self.content)
        self.graphicsElement.textChanged.connect(self.onTextChanged)

    def updateGraphicsElement(self):
        self.graphicsElement.setPlainText(self.content)

    def onTextChanged(self, text: str):
        self.content = text
