from random import random

import pytest
from PyQt5.QtCore import QPoint, QPointF, Qt
from PyQt5.QtWidgets import QGraphicsView, QMainWindow
from pytestqt.qtbot import QtBot

from nodedge.edge import Edge
from nodedge.editor_widget import EditorWidget
from nodedge.mdi_window import MdiWindow
from nodedge.node import Node


@pytest.fixture
def emptyScene(qtbot):
    window = QMainWindow()
    editor = EditorWidget(window)
    window.show()
    qtbot.addWidget(editor)

    return editor.scene


@pytest.fixture
def filledScene(emptyScene):
    node = Node(emptyScene, "", [1], [1])  # noqa: F841
    edge = Edge(emptyScene, node.inputSockets[0], node.outputSockets[0])  # noqa: F841

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


# noinspection PyProtectedMember
def test_addHasBeenModifiedListener(emptyScene):
    assert len(emptyScene._hasBeenModifiedListeners) == 0
    emptyScene.addHasBeenModifiedListener(Node)
    assert len(emptyScene._hasBeenModifiedListeners) > 0


# noinspection PyProtectedMember
def test_addDropListener(qtbot):
    window = QMainWindow()  # noqa: F841
    editor = EditorWidget()
    qtbot.addWidget(editor)
    scene = editor.scene

    assert len(scene.view._dropListeners) == 0
    scene.addDropListener(Node)
    assert len(scene.view._dropListeners) > 0


# noinspection PyProtectedMember
def test_addItemsDeselectedListeners(qtbot):
    window = QMainWindow()  # noqa: F841
    editor = EditorWidget()
    qtbot.addWidget(editor)
    scene = editor.scene

    assert len(scene._itemsDeselectedListeners) == 0
    scene.addItemsDeselectedListener(Node)
    assert len(scene._itemsDeselectedListeners) > 0


# noinspection PyProtectedMember
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


def test_serializeSelected(qtbot):
    window = QMainWindow()
    editor = EditorWidget(window)
    qtbot.addWidget(editor)
    scene = editor.scene
    node = Node(scene, "", [1], [1])  # noqa: F841
    edge = Edge(scene, node.inputSockets[0], node.outputSockets[0])  # noqa: F841

    graphicsEdge = edge.graphicsEdge
    graphicsEdge.setSelected(True)
    graphicsNode = node.graphicsNode
    graphicsNode.setSelected(True)
    assert set(scene.graphicsScene.selectedItems()) <= {graphicsEdge, graphicsNode}

    expectedTitle = "A great title"
    node.title = expectedTitle
    data = scene.clipboard.serializeSelected()

    scene.clear()
    assert scene.nodes == []
    assert scene.edges == []

    scene.clipboard.deserialize(data)

    deserializedNode: Node = scene.nodes[0]
    assert deserializedNode.title == expectedTitle
    deserializedEdge: Edge = scene.edges[0]
    assert deserializedEdge.sourceSocket == deserializedNode.inputSockets[0]
    assert deserializedEdge.targetSocket == deserializedNode.outputSockets[0]


def test_itemAt(qtbot: QtBot):
    window = QMainWindow()
    editor = EditorWidget(window)
    qtbot.addWidget(editor)
    scene = editor.scene
    node = Node(scene, "", [1], [1])  # noqa: F841
    pos = QPoint(10, 10)
    node.pos = pos
    edge = Edge(scene, node.inputSockets[0], node.outputSockets[0])  # noqa: F841

    pos = pos
    assert scene.itemAt(pos).parentItem() == scene.nodes[0].graphicsNode


def test_onSelectedItems(qtbot: QtBot):
    window = MdiWindow()
    window.show()

    subWindow = window.newFile()
    scene = subWindow.widget().scene
    scene.clear()
    subWindow.show()
    node = Node(scene, "", [1], [1])  # noqa: F841
    pos = QPoint(10, 10)
    node.pos = pos

    edge = Edge(scene, node.inputSockets[0], node.outputSockets[0])  # noqa: F841

    window.setActiveSubWindow(subWindow)

    pos2 = subWindow.widget().scene.view.mapToScene(QPoint(-10, -10))
    pos3 = subWindow.widget().scene.view.mapToScene(QPoint(10, 10))
    subWindow.widget().scene.view.show()

    # subWindow.widget().scene.graphicsScene.setFocus(Qt.ActiveWindowFocusReason)
    qtbot.mousePress(
        subWindow.widget(), Qt.LeftButton, pos=QPoint(int(-pos2.x()), int(-pos2.y()))
    )
    qtbot.mouseRelease(
        subWindow.widget(), Qt.LeftButton, pos=QPoint(int(-pos2.x()), int(-pos2.y()))
    )

    assert scene.selectedItems == [node.graphicsNode]
    assert scene.lastSelectedItems == [node.graphicsNode]

    qtbot.mousePress(
        subWindow.widget(), Qt.LeftButton, pos=QPoint(int(-pos3.x()), int(-pos3.y()))
    )
    qtbot.mouseRelease(
        subWindow.widget(), Qt.LeftButton, pos=QPoint(int(-pos3.x()), int(-pos3.y()))
    )
    assert scene.selectedItems == []
    assert scene.lastSelectedItems == []

    subWindow.widget().scene.view.rubberBandDraggingRectangle = True
    qtbot.mousePress(
        subWindow.widget(), Qt.LeftButton, pos=QPoint(int(-pos2.x()), int(-pos2.y()))
    )
    qtbot.mouseRelease(
        subWindow.widget(), Qt.LeftButton, pos=QPoint(int(-pos2.x()), int(-pos2.y()))
    )
    assert scene.selectedItems == [node.graphicsNode]
    assert scene.lastSelectedItems == [node.graphicsNode]


@pytest.mark.parametrize("execution_number", range(5))
def test_undo_crash_without_details(execution_number, qtbot):
    window = MdiWindow()
    window.show()

    subWindow = window.newFile()
    scene = subWindow.widget().scene
    scene.clear()
    scene.history.clear(storeInitialStamp=True)
    subWindow.show()
    print(scene.history.stack)
    node = Node(scene, "", [1], [1])  # noqa: F841
    scene.history.store("Create new node")
    for i in range(5):
        pos = QPointF(random() * 100000, random() * 100000)
        scene.nodes[0].pos = pos
        scene.history.store("Change node position")
        scene.history.undo()
        print(scene.history.currentStep)

    print(scene.history.stackSize)
