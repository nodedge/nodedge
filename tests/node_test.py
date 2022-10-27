import pytest
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QMainWindow

from nodedge.connector import SocketLocation
from nodedge.edge import Edge
from nodedge.editor_widget import EditorWidget
from nodedge.node import Node
from nodedge.scene import Scene
from nodedge.socket_type import SocketType
from nodedge.utils import dumpException


@pytest.fixture
def emptyScene(qtbot):
    window = QMainWindow()
    editor = EditorWidget(window)
    qtbot.addWidget(editor)

    yield editor.scene
    window.close()


@pytest.fixture
def undefinedNode(emptyScene: Scene) -> Node:
    node = Node(emptyScene, inputSocketTypes=[SocketType.Any])  # noqa: F841

    return emptyScene.nodes[0]


@pytest.fixture
def connectedNode(emptyScene: Scene) -> Node:
    node1 = Node(emptyScene, outputSocketTypes=[SocketType.Any])
    node2 = Node(
        emptyScene,
        inputSocketTypes=[SocketType.Any],
        outputSocketTypes=[SocketType.Any],
    )
    node3 = Node(emptyScene, inputSocketTypes=[SocketType.Any])

    edge12 = Edge(
        emptyScene, node1.outputSockets[0], node2.inputSockets[0]
    )  # noqa: F841
    edge23 = Edge(
        emptyScene, node2.outputSockets[0], node3.inputSockets[0]
    )  # noqa: F841

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


def test_socketPos(undefinedNode: Node):
    a = undefinedNode.socketPos(0, SocketLocation.LEFT_TOP, 1)
    assert a == QPointF(-1, 28)


def test_remove(undefinedNode: Node, qtbot):
    try:
        scene = undefinedNode.scene
        undefinedNode.remove()

        assert scene.nodes == []
        # assert undefinedNode.graphicsNode is None
    except Exception as e:
        dumpException(e)


def test_markChildrenDirty(connectedNode: Node):
    childNode = connectedNode.getChildNodes()[0]
    grandChildNode = childNode.getChildNodes()[0]
    assert childNode.isDirty is False
    connectedNode.markChildrenDirty(True)
    assert childNode.isDirty is True
    assert grandChildNode.isDirty is False  # type: ignore


def test_markDescendantsDirty(connectedNode: Node):
    childNode = connectedNode.getChildNodes()[0]
    grandChildNode = childNode.getChildNodes()[0]
    assert childNode.isDirty is False
    connectedNode.markDescendantsDirty(True)
    assert childNode.isDirty is True
    assert grandChildNode.isDirty is True  # type: ignore


def test_markChildrenInvalid(connectedNode: Node):
    childNode = connectedNode.getChildNodes()[0]
    grandChildNode = childNode.getChildNodes()[0]
    assert childNode.isInvalid is False
    connectedNode.markChildrenInvalid(True)
    assert childNode.isInvalid is True
    assert grandChildNode.isInvalid is False  # type: ignore


def test_markDescendantsInvalid(connectedNode: Node):
    childNode = connectedNode.getChildNodes()[0]
    grandChildNode = childNode.getChildNodes()[0]
    assert childNode.isInvalid is False
    connectedNode.markDescendantsInvalid(True)
    assert childNode.isInvalid is True
    assert grandChildNode.isInvalid is True  # type: ignore


def test_eval(undefinedNode: Node):
    undefinedNode.isDirty = True
    undefinedNode.isInvalid = True

    undefinedNode.eval()

    assert undefinedNode.isDirty is False
    assert undefinedNode.isInvalid is False


def test_evalChildren(connectedNode: Node):
    connectedNode.markDescendantsDirty(True)
    connectedNode.markDescendantsInvalid(True)

    connectedNode.evalChildren()

    childNode = connectedNode.getChildNodes()[0]
    grandChildNode = childNode.getChildNodes()[0]
    assert childNode.isDirty is False
    assert childNode.isInvalid is False
    assert grandChildNode.isDirty is True
    assert grandChildNode.isInvalid is True


def test_getChildNodes(emptyScene):
    node1 = Node(emptyScene, outputSocketTypes=[SocketType.Any])
    node2 = Node(
        emptyScene,
        inputSocketTypes=[SocketType.Any],
        outputSocketTypes=[SocketType.Any],
    )
    node3 = Node(emptyScene, inputSocketTypes=[SocketType.Any])

    edge12 = Edge(
        emptyScene, node1.outputSockets[0], node2.inputSockets[0]
    )  # noqa: F841
    edge23 = Edge(
        emptyScene, node2.outputSockets[0], node3.inputSockets[0]
    )  # noqa: F841

    assert node1.getChildNodes() == [node2]
    node2.remove()
    assert node1.getChildNodes() == []


def test_getParentNodes(emptyScene):
    node1 = Node(emptyScene, outputSocketTypes=[SocketType.Any])
    node2 = Node(
        emptyScene,
        inputSocketTypes=[SocketType.Any],
        outputSocketTypes=[SocketType.Any],
    )
    node3 = Node(emptyScene, inputSocketTypes=[SocketType.Any])

    edge12 = Edge(
        emptyScene, node1.outputSockets[0], node2.inputSockets[0]
    )  # noqa: F841
    edge23 = Edge(
        emptyScene, node2.outputSockets[0], node3.inputSockets[0]
    )  # noqa: F841

    assert node2.getParentNodes() == [node1]
    node1.remove()
    assert node2.getParentNodes() == []


def test_inputNodeAt(connectedNode: Node):
    childNode = connectedNode.getChildNodes()[0]

    assert childNode.inputNodeAt(0) == connectedNode

    connectedNode.remove()

    assert childNode.inputNodeAt(0) is None


def test_outputNodesAt(connectedNode: Node):
    scene = connectedNode.scene
    childNode = connectedNode.getChildNodes()[0]
    grandChildNode = childNode.getChildNodes()[0]

    edge = Edge(scene, connectedNode.outputSockets[0], grandChildNode.inputSockets[0])

    assert connectedNode.outputNodesAt(0) == [childNode, grandChildNode]
    childNode.remove()
    assert (
        edge.getOtherSocket(connectedNode.outputSockets[0])
        == grandChildNode.inputSockets[0]
    )
    assert connectedNode.outputNodesAt(0) == [grandChildNode]
