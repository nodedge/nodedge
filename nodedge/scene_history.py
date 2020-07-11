# -*- coding: utf-8 -*-
"""
Scene history module containing :class:`~nodedge.scene_history.SceneHistory` class.
"""

import logging
from typing import Callable, Dict

from nodedge.graphics_edge import GraphicsEdge
from nodedge.graphics_node import GraphicsNode
from nodedge.utils import dumpException


class SceneHistory:
    """
    :class:`~nodedge.scene_history.SceneHistory` class

    It contains the code for storing all the previous actions of the user in a
    dictionary.
    """

    # noinspection PyUnresolvedReferences
    def __init__(
        self, scene: "Scene", maxLength: int = 32  # type: ignore # noqa: F821
    ) -> None:
        """
        :param scene: reference to the :class:`~nodedge.scene.Scene`
        :type scene: :class:`~nodedge.scene.Scene`
        """

        self.scene = scene

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        # Listeners
        self._historyModifiedListeners: list = []
        self._historyStoredListeners: list = []
        self._historyRestoredListeners: list = []

        self._maxLength: int = maxLength
        self._currentStep: int = -1
        self._stack: list = []

    @property
    def currentStep(self) -> int:
        """
        Property representing the current step on the history stack loaded in the scene.

        :return: current step on the history stack
        :rtype: ``int``
        """
        return self._currentStep

    @currentStep.setter
    def currentStep(self, newValue: int):
        if not -1 <= newValue < len(self._stack):
            raise ValueError(
                f"New current step value ({newValue}) is "
                f"out of range: [-1; {len(self._stack)}]"
            )

        if self._currentStep != newValue:
            self._currentStep = newValue

    @property
    def stackSize(self) -> int:
        """
        Number of elements that can be stored in the history stack.

        :return: History stack size
        :rtype: ``int``
        """
        return len(self._stack)

    @property
    def stack(self):
        """
        The stack is a private member of the history,
        it cannot be modified outside of the class.
        This property only has a getter to implement this constraint.


        :return: history stack
        :rtype: ``List[dict]``
        """
        return self._stack

    def addHistoryModifiedListener(self, callback: Callable) -> None:
        """
        Register the callback associated with a `HistoryModified` event.

        :param callback: callback function
        """
        self._historyModifiedListeners.append(callback)

    def addHistoryStoredListener(self, callback: Callable) -> None:
        """
        Register the callback associated with a `HistoryStored` event.

        :param callback: callback function
        """
        self._historyStoredListeners.append(callback)

    def addHistoryRestoredListener(self, callback: Callable) -> None:
        """
        Register the callback associated with a `HistoryRestored` event.

        :param callback: callback function
        """
        self._historyRestoredListeners.append(callback)

    def clear(self, storeInitialStamp: bool = True):
        """
        Reset the history stack.

        :param storeInitialStamp: if True, an initial stamp will be stored in the
            history after cleaning. Otherwise, the history will be empty after cleaning,
            leading to the first actions to be non cancellable.
        :type storeInitialStamp: ``bool``
        """
        self._currentStep = -1
        self._stack = []
        if storeInitialStamp:
            self.storeInitialStamp()

    def __str__(self):
        dlog = (
            f"History [{self._currentStep} / {self.stackSize}, max. {self._maxLength}]"
        )
        for ind, value in enumerate(self._stack):
            dlog += f"\n|||| {ind}: {value['desc']}"

        return dlog

    def storeInitialStamp(self) -> None:
        """
        Helper function usually used when new or open file operations
        are requested.
        """
        self.store("Initial history stamp", sceneIsModified=False)

    @property
    def canUndo(self) -> bool:
        """
        This property returns ``True`` if the undo operation is available for the
        current history stack.

        :rtype: ``bool``
        """
        return self._currentStep > 0

    @property
    def canRedo(self) -> bool:
        """
        This property returns ``True`` if the redo operation is available for the
        current history stack.

        :rtype: ``bool``
        """
        return self._currentStep + 1 < self.stackSize

    def undo(self) -> None:
        """
        Perform the undo operation.
        """
        self.__logger.debug("Undo")

        if self.canUndo:
            self._currentStep -= 1
            self.restore()

    def redo(self) -> None:
        """
        Perform the redo operation
        """
        self.__logger.debug("Redo")

        if self.canRedo:
            self._currentStep += 1
            self.restore()
            self.scene.isModified = True

    def store(self, desc: str, sceneIsModified: bool = True) -> None:
        """
        Store the history stamp into the history stack.

        :param desc: Description of current history stamp
        :type desc: ``str``
        :param sceneIsModified: if ``True`` marks that
            :class:`~nodedge.scene.Scene` has been modified.
        :type sceneIsModified: ``bool``

        Triggers:

        - `History Modified`
        - `History Stored`
        """

        self.__logger.debug(
            f"Storing '{desc}' in history with current step: {self._currentStep} / "
            f"{self.stackSize} "
            f"(max. {self._maxLength})"
        )
        stamp = self._createStamp(desc)

        # If the current step is not at the end of the stack.
        if self.canRedo:
            self._stack = self._stack[0 : self._currentStep + 1]

        # If history is outside of limits
        if self._currentStep + 1 >= self._maxLength:
            self._currentStep -= 1
            self._stack.pop(0)

        self._stack.append(stamp)
        self._currentStep += 1
        self.__logger.debug(f"Setting step to {self._currentStep}")

        self.scene.isModified = sceneIsModified

        # Always trigger history modified event.
        for callback in self._historyModifiedListeners:
            callback()

        for callback in self._historyStoredListeners:
            callback()

    def restore(self) -> None:
        """
        Restore history stamp from history stack.

        Triggers:

        - `History Modified` event
        - `History Restored` event
        """

        self.__logger.debug(
            f"Restoring history with current step: {self._currentStep} / "
            f"{self.stackSize} "
            f"(max. {self._maxLength})"
        )

        self._restoreStamp(self._stack[self._currentStep])

        for callback in self._historyModifiedListeners:
            callback()

        for callback in self._historyRestoredListeners:
            callback()

    def _createStamp(self, desc: str) -> Dict:
        """
        Create a history stamp.
        Internally it serializes the whole scene and the current selection.

        :param desc: Descriptive label for the history stamp
        :return: history stamp serializing the state of the scene
            and the current selection
        :rtype: ``dict``
        """
        selectedObjects: dict = {"nodes": [], "edges": []}

        for item in self.scene.graphicsScene.selectedItems():
            if isinstance(item, GraphicsNode):  # hasattr(item, "node")
                selectedObjects["nodes"].append(item.node.id)
            elif isinstance(item, GraphicsEdge):
                selectedObjects["edges"].append(item.edge.id)

        stamp = {
            "desc": desc,
            "snapshot": self.scene.serialize(),
            "selection": selectedObjects,
        }

        return stamp

    def _restoreStamp(self, stamp: Dict) -> None:
        """
        Restore history stamp to the current scene, included indication of the
        selected items.

        :param stamp: history stamp to restore
        :type stamp: ``dict``
        """
        self.__logger.debug(f"Restoring stamp: {stamp['selection']}")

        try:
            self.scene.deserialize(stamp["snapshot"])

            # Restore the selection
            for edgeId in stamp["selection"]["edges"]:
                for edge in self.scene.edges:
                    if edge.id == edgeId:
                        edge.graphicsEdge.setSelected(True)
                        break

            for nodeId in stamp["selection"]["nodes"]:
                for node in self.scene.nodes:
                    if node.id == nodeId:
                        node.graphicsNode.setSelected(True)
                        break
            self.__logger.debug("History stamp has been restored.")
        except Exception as e:
            self.__logger.warning("Failed to restore stamp")
            dumpException(e)

    def restoreStep(self, step: int) -> None:
        """
        Restore the step of the stack given as argument.

        :param step: index of the stack to be restored
        :type step: ``int``
        """
        self._currentStep = step
        self.restore()
