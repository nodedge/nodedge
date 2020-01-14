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


def test_defaultTitle(undefinedNode: Node):
    undefinedTitle = "Undefined node"
    assert undefinedNode.title == undefinedTitle
    assert undefinedNode.graphicsNode.title == undefinedTitle


def test_setTitle(undefinedNode: Node):
    newTitle = "A coherent title"
    undefinedNode.title = "A coherent title"
    assert undefinedNode.title == newTitle
    assert undefinedNode.graphicsNode.title == newTitle


def test_defaultPos(undefinedNode: Node):
    undefinedPos = QPointF()
    assert undefinedNode.pos == undefinedPos


def test_setPosWithQPointF(undefinedNode: Node):
    expectedPos = QPointF(2.0, 4.0)
    undefinedNode.pos = expectedPos
    assert undefinedNode.pos == expectedPos


def test_setPosWithIterable(undefinedNode: Node):
    expectedPos = QPointF(3.0, 6.0)
    undefinedNode.pos = [expectedPos.x(), expectedPos.y()]
    assert undefinedNode.pos == expectedPos
    expectedPos = QPointF(4.0, 8.0)
    undefinedNode.pos = (expectedPos.x(), expectedPos.y())
    assert undefinedNode.pos == expectedPos


def test_setWrongPos(undefinedNode: Node):
    with pytest.raises(ValueError):
        wrongPos = [1, 2, 3]
        undefinedNode.pos = wrongPos

    with pytest.raises(TypeError):
        stringPos = ["a", "b"]
        undefinedNode.pos = stringPos


def test_defaultIsDirty(undefinedNode: Node):
    expectedValue = False
    assert undefinedNode.isDirty == expectedValue


def test_markIsDirty(undefinedNode: Node):
    expectedValue = True
    undefinedNode.isDirty = expectedValue
    assert undefinedNode.isDirty == expectedValue


def test_defaultIsInvalid(undefinedNode: Node):
    expectedValue = False
    assert undefinedNode.isInvalid == expectedValue


def test_markIsInvalid(undefinedNode: Node):
    expectedValue = True
    undefinedNode.isInvalid = expectedValue
    assert undefinedNode.isInvalid == expectedValue
