from typing import Callable, List, Optional, Union

from PySide6.QtCore import QEvent
from PySide6.QtGui import QAction, QKeySequence, QMouseEvent, Qt
from PySide6.QtWidgets import QInputDialog, QMenu, QTabWidget

from nodedge.dats.worksheets_tab_widget import WorksheetsTabWidget


class WorkbooksTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.workbooks: List[WorksheetsTabWidget] = []

        self.setTabsClosable(True)
        self.setMovable(True)
        self.setElideMode(Qt.ElideRight)  # type: ignore
        self.setUsesScrollButtons(True)

        self.addWorkbook()

        self.tabBar = self.tabBar()
        self.tabBar.installEventFilter(self)
        self.clickedIndex = None

        self.tabBarDoubleClicked.connect(self.renameWorkbook)  # type: ignore
        self.tabCloseRequested.connect(self.removeWorkbook)  # type: ignore

        self.createActions()

    # noinspection DuplicatedCode
    def eventFilter(self, watched, event):
        if watched == self.tabBar:
            if event.type() == QEvent.MouseButtonPress:
                event: QMouseEvent
                if event.button() == Qt.RightButton:  # type: ignore
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
            "&Create",
            self.addWorkbook,
            "Create worksheet",
            QKeySequence("Ctrl+Shift+N"),
        )

        self.closeAct = self.createAction(
            "&Close",
            self.removeWorkbook,
            "Close worksheet",
            QKeySequence("Ctrl+Shift+W"),
        )

        self.renameAct = self.createAction(
            "&Rename",
            self.renameWorkbook,
            "rename workbook",
            QKeySequence("Shift+F2"),
        )

    def addWorkbook(self, workbookName="Workbook1") -> WorksheetsTabWidget | None:
        if isinstance(workbookName, bool):
            workbookName, ok = QInputDialog.getText(
                self, "Enter workbook name", "Workbook name"
            )

            if not ok:
                return None

        worksheetsTabWidget = WorksheetsTabWidget(workbookName=workbookName)

        self.addTab(worksheetsTabWidget, workbookName)
        self.workbooks.append(worksheetsTabWidget)

        return worksheetsTabWidget

    def removeWorkbook(self, index=None):
        if index is None:
            index = self.clickedIndex
        self.removeTab(index)
        self.workbooks.pop(index)

    def renameWorkbook(self, index=None, name=None):
        if index is None:
            index = self.clickedIndex
        if name is None:
            name, ok = QInputDialog.getText(
                self, "Enter workbook name", "Workbook name"
            )

            if not ok:
                return
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
