import pytest
from PyQt5.QtCore import QPointF
from PyQt5.QtWidgets import QMainWindow

from nodedge.editor_widget import EditorWidget
from nodedge.node import Node


@pytest.fixture
def emptyScene(qtbot):
    window = QMainWindow()
    editor = EditorWidget(window)
    qtbot.addWidget(editor)

    return editor.scene


@pytest.fixture
def undefinedNode(emptyScene) -> Node:
    node = Node(emptyScene)  # noqa: F841

    return emptyScene.nodes[0]


def test_titleProperty(undefinedNode: Node):
    undefinedTitle = "Undefined node"
    assert undefinedNode.title == undefinedTitle
    assert undefinedNode.graphicsNode.title == undefinedTitle
    newTitle = "A coherent title"
    undefinedNode.title = "A coherent title"
    assert undefinedNode.title == newTitle
    assert undefinedNode.graphicsNode.title == newTitle


def test_posProperty(undefinedNode: Node):
    undefinedPos = QPointF()
    assert undefinedNode.pos == undefinedPos
    expectedPos = QPointF(2.0, 4.0)
    undefinedNode.pos = expectedPos
    assert undefinedNode.pos == expectedPos
    expectedPos = QPointF(3.0, 6.0)
    undefinedNode.pos = [expectedPos.x(), expectedPos.y()]
    assert undefinedNode.pos == expectedPos
    expectedPos = QPointF(4.0, 8.0)
    undefinedNode.pos = (expectedPos.x(), expectedPos.y())
    assert undefinedNode.pos == expectedPos

    wrongPos = [1, 2, 3]
    with pytest.raises(ValueError):
        undefinedNode.pos = wrongPos

    stringPos = ["a", "b"]
    with pytest.raises(TypeError):
        undefinedNode.pos = stringPos
