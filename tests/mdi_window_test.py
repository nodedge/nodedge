import pytest
from PyQt5.QtWidgets import QMessageBox
from pytestqt.qtbot import QtBot

from nodedge.mdi_window import MdiWindow


@pytest.fixture
def emptyMdiWindow(qtbot: QtBot):
    return MdiWindow()


@pytest.fixture
def filledMdiWindow(qtbot):
    window = MdiWindow()
    window.show()
    subWindow = window.newFile()
    return window


def test_newFile(emptyMdiWindow):
    subWindow = emptyMdiWindow.newFile()
    emptyMdiWindow.mdiArea.setActiveSubWindow(subWindow)

    assert emptyMdiWindow.mdiArea.subWindowList() == [subWindow]


def test_setActiveSubWindow(qtbot: QtBot, filledMdiWindow: MdiWindow):
    subWindow = filledMdiWindow.mdiArea.subWindowList()[0]
    filledMdiWindow.mdiArea.setActiveSubWindow(subWindow)

    with qtbot.waitActive(subWindow, timeout=10):
        assert filledMdiWindow.mdiArea.activeSubWindow() == subWindow


def test_closeSubWindow(qtbot: QtBot, mocker):
    mocker.patch.object(QMessageBox, "warning", return_value=QMessageBox.Discard)
    window = MdiWindow()
    window.show()
    window.newFile()
    window.close()

    assert window.mdiArea.subWindowList() == []
