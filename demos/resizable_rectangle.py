# -*- coding: utf-8 -*-
"""
resizable_rectangle.py module containing :class:`~nodedge.resizable_rectangle.py.<ClassName>` class.
"""

import typing

from PySide6.QtCore import QRectF, QSize
from PySide6.QtGui import QBrush, QColor, QPen, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsItem,
    QGraphicsRectItem,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)


class ResizableRect(QGraphicsRectItem):
    def __init__(self, *args):
        super().__init__(*args)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setPen(QPen(QBrush(QColor("blue")), 5))
        self.selected_edge = None
        self.click_pos = self.click_rect = None

    def mousePressEvent(self, event):
        """The mouse is pressed, start tracking movement."""
        self.click_pos = event.pos()
        rect = self.rect()
        if abs(rect.left() - self.click_pos.x()) < 5:
            self.selected_edge = "left"
        elif abs(rect.right() - self.click_pos.x()) < 5:
            self.selected_edge = "right"
        elif abs(rect.top() - self.click_pos.y()) < 5:
            self.selected_edge = "top"
        elif abs(rect.bottom() - self.click_pos.y()) < 5:
            self.selected_edge = "bottom"
        else:
            self.selected_edge = None
        self.click_pos = event.pos()
        self.click_rect = rect
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Continue tracking movement while the mouse is pressed."""
        # Calculate how much the mouse has moved since the click.
        pos = event.pos()
        x_diff = pos.x() - self.click_pos.x()
        y_diff = pos.y() - self.click_pos.y()

        # Start with the rectangle as it was when clicked.
        rect = QRectF(self.click_rect)

        # Then adjust by the distance the mouse moved.
        if self.selected_edge is None:
            rect.translate(x_diff, y_diff)
        elif self.selected_edge == "top":
            rect.adjust(0, y_diff, 0, 0)
        elif self.selected_edge == "left":
            rect.adjust(x_diff, 0, 0, 0)
        elif self.selected_edge == "bottom":
            rect.adjust(0, 0, 0, y_diff)
        elif self.selected_edge == "right":
            rect.adjust(0, 0, x_diff, 0)

        # Figure out the limits of movement. I did it by updating the scene's
        # rect after the window resizes.
        scene_rect = self.scene().sceneRect()
        view_left = scene_rect.left()
        view_top = scene_rect.top()
        view_right = scene_rect.right()
        view_bottom = scene_rect.bottom()

        # Next, check if the rectangle has been dragged out of bounds.
        if rect.top() < view_top:
            if self.selected_edge is None:
                rect.translate(0, view_top - rect.top())
            else:
                rect.setTop(view_top)
        if rect.left() < view_left:
            if self.selected_edge is None:
                rect.translate(view_left - rect.left(), 0)
            else:
                rect.setLeft(view_left)
        if view_bottom < rect.bottom():
            if self.selected_edge is None:
                rect.translate(0, view_bottom - rect.bottom())
            else:
                rect.setBottom(view_bottom)
        if view_right < rect.right():
            if self.selected_edge is None:
                rect.translate(view_right - rect.right(), 0)
            else:
                rect.setRight(view_right)

        # Also check if the rectangle has been dragged inside out.
        if rect.width() < 5:
            if self.selected_edge == "left":
                rect.setLeft(rect.right() - 5)
            else:
                rect.setRight(rect.left() + 5)
        if rect.height() < 5:
            if self.selected_edge == "top":
                rect.setTop(rect.bottom() - 5)
            else:
                rect.setBottom(rect.top() + 5)

        # Finally, update the rect that is now guaranteed to stay in bounds.
        self.setRect(rect)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        central = QWidget(self)
        self.setCentralWidget(central)

        self.rect = ResizableRect()
        scene = QGraphicsScene(0, 0, 300, 300)
        scene.addItem(self.rect)
        self.view = QGraphicsView(central)
        self.view.setScene(scene)

        layout = QVBoxLayout(central)
        self.setLayout(layout)
        layout.addWidget(self.view)

        self.old_size: typing.Optional[QSize] = None

    def show(self):
        super().show()
        self.resize_scene()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        self.resize_scene()

    def resize_scene(self):
        if not self.isVisible():
            # Viewport size isn't set yet, so calculation won't work.
            return
        size = self.view.maximumViewportSize()
        if self.old_size is None:
            new_rect = QRectF(
                size.width() / 4, size.height() / 4, size.width() / 2, size.height() / 2
            )
        else:
            old_rect = QRectF(self.rect.rect())
            x_scale = size.width() / self.old_size.width()
            y_scale = size.height() / self.old_size.height()
            new_rect = QRectF(
                old_rect.left() * x_scale,
                old_rect.top() * y_scale,
                old_rect.width() * x_scale,
                old_rect.height() * y_scale,
            )
        self.rect.setRect(new_rect)
        self.view.scene().setSceneRect(0, 0, size.width(), size.height())
        self.old_size = size


def main():
    app = QApplication()
    window = MainWindow()
    window.show()

    app.exec_()


main()
