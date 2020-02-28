# -*- coding: utf-8 -*-
"""
A module containing all code for working with History (Undo/Redo)
"""

import logging

from nodedge.graphics_edge import GraphicsEdge
from nodedge.utils import dumpException


class SceneHistory:
    """Class contains all the code for undo/redo operations"""

    def __init__(self, scene: "Scene", maxLength: int = 32) -> None:  # type: ignore # noqa: F821
        """
        :param scene: Reference to the :class:`~nodedge.scene.Scene`
        :type scene: :class:`~nodedge.scene.Scene`

        :Instance Attributes:

        - **scene** - reference to the :class:`~nodedge.scene.Scene`
        - **history_limit** - number of history steps that can be stored
        """

        self.scene = scene

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.DEBUG)

        # Listeners
        self._historyModifiedListeners: list = []
        self._historyStoredListeners: list = []
        self._historyRestoredListeners: list = []

        self._maxLength = maxLength
        self.currentStep = -1
        self.stack: list = []

    def addHistoryModifiedListener(self, callback):
        """
        Register callback for `HistoryModified` event

        :param callback: callback function
        """
        self._historyModifiedListeners.append(callback)

    def addHistoryStoredListener(self, callback):
        """
        Register callback for `HistoryStored` event

        :param callback: callback function
        """
        self._historyStoredListeners.append(callback)

    def addHistoryRestoredListener(self, callback):
        """
        Register callback for `HistoryRestored` event

        :param callback: callback function
        """
        self._historyRestoredListeners.append(callback)

    def clear(self, storeInitialStamp=True):
        """Reset the history stack"""
        self.currentStep = -1
        self.stack = []
        if storeInitialStamp:
            self.scene.history.storeInitialStamp()

    def __str__(self):
        dlog = (
            f"History [{self.currentStep} / {len(self.stack)}, max. {self._maxLength}]"
        )
        for ind, value in enumerate(self.stack):
            dlog += f"\n|||| {ind}: {value['desc']}"

        return dlog

    def storeInitialStamp(self):
        """Helper function usually used when new or open file requested"""
        self.store("Initial history stamp", sceneIsModified=False)

    @property
    def canUndo(self) -> bool:
        """Return ``True`` if Undo is available for current `History Stack`

        :rtype: ``bool``
        """
        return self.currentStep > 0

    @property
    def canRedo(self) -> bool:
        """
        Return ``True`` if Redo is available for current `History Stack`

        :rtype: ``bool``
        """
        return self.currentStep + 1 < len(self.stack)

    def undo(self):
        """Undo operation"""
        self.__logger.debug("Undo")

        if self.canUndo:
            self.currentStep -= 1
            self.restore()

    def redo(self):
        """Redo operation"""
        self.__logger.debug("Redo")

        if self.canRedo:
            self.currentStep += 1
            self.restore()
            self.scene.isModified = True

    def store(self, desc, sceneIsModified=True):
        """
        Store History Stamp into History Stack

        :param desc: Description of current History Stamp
        :type desc: ``str``
        :param sceneIsModified: if ``True`` marks :class:`~nodedge.scene.Scene` with `has_been_modified`
        :type sceneIsModified: ``bool``

        Triggers:

        - `History Modified`
        - `History Stored`
        """

        self.__logger.debug(
            f"Storing '{desc}' in history with current step: {self.currentStep} / {len(self.stack)} "
            f"(max. {self._maxLength})"
        )
        stamp = self._createStamp(desc)

        # If the current step is not at the end of the stack.
        if self.canRedo:
            self.stack = self.stack[0 : self.currentStep + 1]

        # If history is outside of limits
        if self.currentStep + 1 >= self._maxLength:
            self.currentStep -= 1
            self.stack.pop(0)

        self.stack.append(stamp)
        self.currentStep += 1
        self.__logger.debug(f"Setting step to {self.currentStep}")

        self.scene.isModified = sceneIsModified

        # Always trigger history modified event.
        for callback in self._historyModifiedListeners:
            callback()

        for callback in self._historyStoredListeners:
            callback()

    def restore(self):
        """
        Restore `History Stamp` from `History stack`.

        Triggers:

        - `History Modified` event
        - `History Restored` event
        """

        self.__logger.debug(
            f"Restoring history with current step: {self.currentStep} / {len(self.stack)} "
            f"(max. {self._maxLength})"
        )

        self._restoreStamp(self.stack[self.currentStep])

        for callback in self._historyModifiedListeners:
            callback()

        for callback in self._historyRestoredListeners:
            callback()

    def _createStamp(self, desc):
        """
        Create History Stamp. Internally serialize whole scene and current selection

        :param desc: Descriptive label for the History Stamp
        :return: History stamp serializing state of `Scene` and current selection
        :rtype: ``dict``
        """
        selectedObjects = {"blocks": [], "edges": []}

        for item in self.scene.graphicsScene.selectedItems():
            if hasattr(item, "node"):
                selectedObjects["blocks"].append(item.node.id)
            elif isinstance(item, GraphicsEdge):
                selectedObjects["edges"].append(item.edge.id)

        stamp = {
            "desc": desc,
            "snapshot": self.scene.serialize(),
            "selection": selectedObjects,
        }

        return stamp

    def _restoreStamp(self, stamp):
        """
        Restore History Stamp to current `Scene` with selection of items included

        :param stamp: History Stamp to restore
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

            for nodeId in stamp["selection"]["blocks"]:
                for node in self.scene.nodes:
                    if node.id == nodeId:
                        node.graphicsNode.setSelected(True)
                        break
        except Exception as e:
            self.__logger.warning("Failed to restore stamp")
            dumpException(e)
