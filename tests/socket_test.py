import pytest
from PySide6.QtWidgets import QMainWindow

from nodedge.editor_widget import EditorWidget
from nodedge.node import Node
from nodedge.scene import Scene


@pytest.fixture
def emptyScene(qtbot):
    window = QMainWindow()
    editor = EditorWidget(window)
    qtbot.addWidget(editor)

    yield editor.scene
    window.close()


@pytest.fixture
def undefinedNode(emptyScene: Scene) -> Node:
    node = Node(emptyScene)  # noqa: F841

    return emptyScene.nodes[0]
