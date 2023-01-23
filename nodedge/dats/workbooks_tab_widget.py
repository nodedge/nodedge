from __future__ import annotations

from typing import Callable, List, Optional, Union

from PySide6.QtCore import QEvent
from PySide6.QtGui import QAction, QKeySequence, QMouseEvent, Qt
from PySide6.QtWidgets import QInputDialog, QMenu, QTabWidget

from nodedge.dats.worksheets_tab_widget import WorksheetsTabWidget


class WorkbooksTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.window = parent
        self.workbooks: List[WorksheetsTabWidget] = []

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setElideMode(Qt.ElideRight)
        self.setUsesScrollButtons(True)

        self.addWorkbook()

        self.tabBar = self.tabBar()
        self.tabBar.installEventFilter(self)
        self.clickedIndex = None

        self.tabBarDoubleClicked.connect(self.renameWorkbook)
        self.tabCloseRequested.connect(self.removeWorkbook)

        self.createActions()

    # noinspection DuplicatedCode
    def eventFilter(self, watched, event):
        if watched == self.tabBar:
            if event.type() == QEvent.MouseButtonPress:
                event: QMouseEvent
                if event.button() == Qt.RightButton:
                    self.openContextMenu(event.pos(), event.globalPos())

        return super().eventFilter(watched, event)

    def openContextMenu(self, pos, globalPos):
        self.clickedIndex = self.tabBar.tabAt(pos)

        menu = QMenu()
        menu.addAction(self.createAct)
        menu.addAction(self.renameAct)
        menu.addAction(self.closeAct)

        menu.exec(globalPos)

    # noinspection PyAttributeOutsideInit
    def createActions(self):
        self.createAct = self.createAction(
            "&Add workbook",
            self.addWorkbook,
            "Add workbook",
        )

        self.closeAct = self.createAction(
            "&Close",
            self.removeWorkbook,
            "Close worksheet",
        )

        self.renameAct = self.createAction(
            "&Rename",
            self.renameWorkbook,
            "rename workbook",
            QKeySequence("Shift+F2"),
        )

    def addWorkbook(self, workbookName="Workbook1") -> WorksheetsTabWidget | None:
        if isinstance(workbookName, bool):
            dlg = QInputDialog(self)
            dlg.setWindowTitle("Enter new workbook name")
            dlg.setLabelText("Name:")
            dlg.setInputMode(QInputDialog.TextInput)
            dlg.setLabelText("Workbook name:")
            dlg.resize(500, 100)
            ok = dlg.exec_()
            workbookName = dlg.textValue()

            if not ok:
                return None

        worksheetsTabWidget = WorksheetsTabWidget(
            parent=self, workbookName=workbookName
        )

        self.addTab(worksheetsTabWidget, workbookName)
        self.workbooks.append(worksheetsTabWidget)

        return worksheetsTabWidget

    def removeWorkbook(self, index=None):
        if index is None:
            if self.clickedIndex is not None:
                index = self.clickedIndex
            else:
                index = self.currentIndex()
        self.removeTab(index)
        self.workbooks.pop(index)

    def renameWorkbook(self, index=None, name=None):
        if index is None:
            index = self.clickedIndex
        if name is None:
            dlg = QInputDialog(self)
            dlg.setWindowTitle("Enter new workbook name")
            dlg.setLabelText("Name:")
            dlg.setInputMode(QInputDialog.TextInput)
            dlg.setLabelText("Workbook name:")
            dlg.resize(500, 100)
            ok = dlg.exec_()

            if not ok:
                return
            name = dlg.textValue()
        self.setTabText(index, name)
        self.workbooks[index].name = name

    def createAction(
        self,
        name: str,
        callback: Callable,
        statusTip: Optional[str] = None,
        shortcut: Union[None, str, QKeySequence] = None,
    ) -> QAction:
        """
        Create an action for this window and add it to actions list.

        :param name: action's name
        :type name: ``str``
        :param callback: function to be called when the action is triggered
        :type callback: ``Callable``
        :param statusTip: Description of the action displayed
            at the bottom left of the application.
        :type statusTip: Optional[``str``]
        :param shortcut: Keyboard shortcut to trigger the action.
        :type shortcut: ``Optional[str]``
        :return:
        """
        act = QAction(name, self)
        act.triggered.connect(callback)  # type: ignore

        if statusTip is not None:
            act.setStatusTip(statusTip)
            act.setToolTip(statusTip)

        if shortcut is not None:
            act.setShortcut(QKeySequence(shortcut))

        self.addAction(act)

        return act

    # def mousePressEvent(self, event: QMouseEvent) -> None:
    #     if event.button() == Qt.RightButton:
    #         a = QMenu(self)
    #         self.createAction("&Create",
    #                           self.addWorksheet,
    #                           "Create worksheet",
    #                           QKeySequence("Ctrl+N"), )
    #         a.addAction("Create new worksheet")
    #         a.popup(event.globalPosition().toPoint())
    #
    #
    #         super().mousePressEvent(event)

    def updateXAxis(self, minValue: int, maxValue: int):
        """
        Update the x-axis of the chart.

        :param min: minimum value of the x-axis
        :type min: ``int``
        :param max: maximum value of the x-axis
        :type max: ``int``
        """
        for workbook in self.workbooks:
            for worksheet in workbook.worksheets:
                worksheet.updateXAxis(minValue, maxValue)
