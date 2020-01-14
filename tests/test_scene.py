import pytest

from PyQt5.QtWidgets import QMainWindow, QGraphicsView

from nodedge.editor_widget import EditorWidget
from nodedge.node import Node
from nodedge.edge import Edge


@pytest.fixture
def emptyScene(qtbot):
    window = QMainWindow()
    editor = EditorWidget(window)
    qtbot.addWidget(editor)

    return editor.scene


@pytest.fixture
def filledScene(emptyScene):
    node = Node(emptyScene)
    edge = Edge(emptyScene)

    return emptyScene


def test_emptySceneIsNotModifiedYet(emptyScene):
    assert emptyScene.isModified is False


def test_sceneHasView(qtbot):
    window = QMainWindow()
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


def test_sceneClear(filledScene):
    assert len(filledScene.nodes) > 0
    filledScene.clear()
    assert filledScene.nodes == []
    assert filledScene.edges == []
    assert filledScene.isModified is False


def test_sceneAddHasBeenModifiedListener(emptyScene):
    assert len(emptyScene._hasBeenModifiedListeners) == 0
    emptyScene.addHasBeenModifiedListener(Node)
    assert len(emptyScene._hasBeenModifiedListeners) > 0


def test_sceneAddDropListener(qtbot):
    window = QMainWindow()
    editor = EditorWidget()
    qtbot.addWidget(editor)
    scene = editor.scene

    assert len(scene.view._dropListeners) == 0
    scene.addDropListener(Node)
    assert len(scene.view._dropListeners) > 0


def test_sceneAddItemsDeselectedListeners(qtbot):
    window = QMainWindow()
    editor = EditorWidget()
    qtbot.addWidget(editor)
    scene = editor.scene

    assert len(scene._itemsDeselectedListeners) == 0
    scene.addItemsDeselectedListener(Node)
    assert len(scene._itemsDeselectedListeners) > 0


def test_sceneAddItemSelectedListeners(qtbot):
    window = QMainWindow()
    editor = EditorWidget()
    qtbot.addWidget(editor)
    scene = editor.scene

    assert len(scene._itemSelectedListeners) == 0
    scene.addItemSelectedListener(Node)
    assert len(scene._itemSelectedListeners) > 0
