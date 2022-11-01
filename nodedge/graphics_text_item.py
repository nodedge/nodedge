# -*- coding: utf-8 -*-
"""
${FILE_NAME} module containing :class:`~nodedge.${FILE_NAME}.<ClassName>` class.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFocusEvent
from PySide6.QtWidgets import (
    QFontDialog,
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
    QGraphicsTextItem,
)


class GraphicsTextItem(QGraphicsTextItem):
    textChanged = Signal(str)

    def __init__(self, element, *args):
        """
        Initialize the shape.
        """
        super().__init__(*args)

        self.element = element

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsItem.ItemIsFocusable)

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.setTextInteractionFlags(Qt.TextEditorInteraction)
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self.setCursor(Qt.IBeamCursor)
        # self.setTextCursor()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        cursor = self.textCursor()
        cursor.clearSelection()
        self.setTextCursor(cursor)
        self.setCursor(Qt.OpenHandCursor)
        self.textChanged.emit(self.toPlainText())  # type: ignore

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.cursor().shape() != Qt.IBeamCursor:
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self.cursor().shape() != Qt.IBeamCursor:
            self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

        if event.button() == Qt.RightButton:
            ok, font = QFontDialog.getFont()
            if not ok:
                return
            print(font)
            self.setFont(font)
