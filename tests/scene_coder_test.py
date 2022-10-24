import pytest
from PySide6.QtWidgets import QMainWindow

from nodedge.blocks.autogen.operator.add_block import AddBlock
from nodedge.blocks.custom.input_block import InputBlock
from nodedge.blocks.custom.output_block import OutputBlock
from nodedge.edge import Edge
from nodedge.editor_widget import EditorWidget
from nodedge.utils import indentCode


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
    expectedResult = (
        "var_0 = 2.0\n"
        + "var_1 = 1.0\n"
        + "var_2 = add(var_1, var_0)\n"
        + "return [var_2]"
    )

    _, generatedCode = filledScene.coder.generateCode()

    assert generatedCode == expectedResult


def test_addImports(filledScene):
    orderedNodeList, generatedCode = filledScene.coder.generateCode()

    filename = "unnamed"
    imports = "from operator import add\n\n\n"

    expectedResult = (
        imports
        + f"def {filename}():"
        + indentCode(generatedCode)
        + f"\n\n\nif __name__ == '__main__':\n    {filename}()\n"
    )

    generatedFileString = filledScene.coder.addImports(orderedNodeList, generatedCode)

    assert generatedFileString == expectedResult
