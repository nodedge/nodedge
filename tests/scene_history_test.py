# -*- coding: utf-8 -*-
"""
<ModuleName> module containing :class:`~nodedge.<Name>.<ClassName>` class.
"""

import pytest
from PySide6.QtWidgets import QMainWindow

from nodedge.editor_widget import EditorWidget
from nodedge.scene_history import SceneHistory
from tests import not_raises


@pytest.fixture
def emptyScene(qtbot):
    window = QMainWindow()
    editor = EditorWidget(window)
    window.show()
    qtbot.addWidget(editor)

    yield editor.scene
    window.close()


@pytest.fixture
def emptyHistory(emptyScene):
    return SceneHistory(emptyScene)


@pytest.fixture
def filledHistory(emptyHistory):

    emptyHistory.store(desc="First action")
    emptyHistory.store(desc="Second action")
    emptyHistory.store(desc="Third action")

    return emptyHistory


def test_newHistory(emptyHistory):
    assert emptyHistory.currentStep == -1


def test_currentStep(filledHistory):
    assert filledHistory.currentStep == 2

    with not_raises(ValueError):
        filledHistory.currentStep = 1

    with not_raises(ValueError):
        filledHistory.currentStep = -1

    with pytest.raises(ValueError):
        filledHistory.currentStep = 3

    with pytest.raises(ValueError):
        filledHistory.currentStep = -2


def test_clear_without_initial_stamp(filledHistory):
    assert filledHistory.stackSize == 3

    filledHistory.clear(storeInitialStamp=False)

    assert filledHistory.stackSize == 0
    assert filledHistory.currentStep == -1


def test_clear_with_initial_stamp(filledHistory):
    filledHistory.clear()

    assert filledHistory.stackSize == 1
    assert filledHistory.currentStep == 0


def test_undo(filledHistory):
    assert filledHistory.currentStep == 2
    assert filledHistory.stackSize == 3
    filledHistory.undo()
    assert filledHistory.currentStep == 1
    assert filledHistory.stackSize == 3


def test_redo(filledHistory):
    assert filledHistory.currentStep == 2
    assert filledHistory.stackSize == 3
    filledHistory.undo()
    filledHistory.redo()
    assert filledHistory.currentStep == 2
    assert filledHistory.stackSize == 3


def test_store(emptyHistory):
    assert emptyHistory.currentStep == -1
    assert emptyHistory.stackSize == 0
    emptyHistory.scene.isModified = False
    emptyHistory.store("An action")
    assert emptyHistory.currentStep == 0
    assert emptyHistory.stackSize == 1
    assert emptyHistory.scene.isModified is True
    emptyHistory.scene.isModified = False
    emptyHistory.store("Another action", sceneIsModified=False)
    assert emptyHistory.currentStep == 1
    assert emptyHistory.stackSize == 2
    assert emptyHistory.scene.isModified is False


def test_restoreStep(filledHistory):
    filledHistory.scene.isModified = False
    expectedStep = 1
    initialStackSize = filledHistory.stackSize
    filledHistory.restoreStep(expectedStep)
    assert filledHistory.currentStep == expectedStep
    assert filledHistory.stackSize == initialStackSize
