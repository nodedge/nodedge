import pytest
from PySide2.QtWidgets import QMainWindow

from nodedge.blocks import AddBlock, InputBlock, OutputBlock
from nodedge.edge import Edge
from nodedge.editor_widget import EditorWidget


@pytest.fixture
def emptyScene(qtbot):
    window = QMainWindow()
    editor = EditorWidget(window)
    window.show()
    qtbot.addWidget(editor)

    yield editor.scene
    window.close()


@pytest.fixture
def filledScene(emptyScene):
    inputBlock1: InputBlock = InputBlock(emptyScene)  # noqa: F841
    inputBlock1.content.edit.setText(str(1))
    inputBlock2: InputBlock = InputBlock(emptyScene)  # noqa: F841
    inputBlock2.content.edit.setText(str(2))
    addBlock: AddBlock = AddBlock(emptyScene)
    edgeIn1Add: Edge = Edge(
        emptyScene, inputBlock1.outputSockets[0], addBlock.inputSockets[0]
    )  # noqa: F841
    edgeIn2Add: Edge = Edge(
        emptyScene, inputBlock2.outputSockets[0], addBlock.inputSockets[1]
    )  # noqa: F841
    outputBlock: OutputBlock = OutputBlock(emptyScene)
    edgeAddOut: Edge = Edge(
        emptyScene, addBlock.outputSockets[0], outputBlock.inputSockets[0]
    )  # noqa: F841

    # Reset isModified property
    emptyScene.isModified = False

    return emptyScene


def test_generateCode(filledScene):
    expectedResult = "var_0 = 2.0\n" + \
                     "var_1 = 1.0\n" + \
                     "var_2 = add(var_1, var_0)\n" + \
                     "return [var_2]"

    assert filledScene.coder.generateCode() == expectedResult
