import pytest
from PyQt5.QtWidgets import QGraphicsView, QMainWindow

from nodedge.edge import Edge
from nodedge.editor_widget import EditorWidget
from nodedge.node import Node


@pytest.fixture
def emptyScene(qtbot):
    window = QMainWindow()
    editor = EditorWidget(window)
    qtbot.addWidget(editor)

    return editor.scene


@pytest.fixture
def filledScene(emptyScene):
    node = Node(emptyScene)  # noqa: F841
    edge = Edge(emptyScene)  # noqa: F841

    return emptyScene


def test_emptySceneIsNotModifiedYet(emptyScene):
    assert emptyScene.isModified is False


def test_sceneHasView(qtbot):
    window = QMainWindow()  # noqa: F841
    editor = EditorWidget()
    qtbot.addWidget(editor)

    assert isinstance(editor.scene.view, QGraphicsView)


def test_emptySceneAddAndRemoveNode(emptyScene):
    node = Node(emptyScene)
    assert node in emptyScene.nodes
    emptyScene.removeNode(node)
    assert emptyScene.nodes == []
    emptyScene.addNode(node)
    assert node in emptyScene.nodes
    emptyScene.removeNode(node)
    assert emptyScene.nodes == []


def test_emptySceneAddAndRemoveEdge(emptyScene):
    edge = Edge(emptyScene)
    assert edge in emptyScene.edges
    emptyScene.removeEdge(edge)
    assert emptyScene.edges == []
    emptyScene.addEdge(edge)
    assert edge in emptyScene.edges
    emptyScene.removeEdge(edge)
    assert emptyScene.edges == []


def test_clear(filledScene):
    assert len(filledScene.nodes) > 0
    filledScene.clear()
    assert filledScene.nodes == []
    assert filledScene.edges == []
    assert filledScene.isModified is False


def test_addHasBeenModifiedListener(emptyScene):
    assert len(emptyScene._hasBeenModifiedListeners) == 0
    emptyScene.addHasBeenModifiedListener(Node)
    assert len(emptyScene._hasBeenModifiedListeners) > 0


def test_addDropListener(qtbot):
    window = QMainWindow()  # noqa: F841
    editor = EditorWidget()
    qtbot.addWidget(editor)
    scene = editor.scene

    assert len(scene.view._dropListeners) == 0
    scene.addDropListener(Node)
    assert len(scene.view._dropListeners) > 0


def test_addItemsDeselectedListeners(qtbot):
    window = QMainWindow()  # noqa: F841
    editor = EditorWidget()
    qtbot.addWidget(editor)
    scene = editor.scene

    assert len(scene._itemsDeselectedListeners) == 0
    scene.addItemsDeselectedListener(Node)
    assert len(scene._itemsDeselectedListeners) > 0


def test_addItemSelectedListeners(qtbot):
    window = QMainWindow()  # noqa: F841
    editor = EditorWidget()
    qtbot.addWidget(editor)
    scene = editor.scene

    assert len(scene._itemSelectedListeners) == 0
    scene.addItemSelectedListener(Node)
    assert len(scene._itemSelectedListeners) > 0


def test_resetLastSelectedStates(filledScene):
    filledScene.nodes[0].graphicsNode.selectedState = True
    filledScene.edges[0].graphicsEdge.selectedState = True

    filledScene.resetLastSelectedStates()

    assert filledScene.nodes[0].graphicsNode.selectedState is False
    assert filledScene.edges[0].graphicsEdge.selectedState is False
