# -*- coding: utf-8 -*-
"""
Scene history module containing :class:`~nodedge.scene_history.SceneHistory` class.
"""

import logging

from nodedge.graphics_edge import GraphicsEdge
from nodedge.utils import dumpException


class SceneHistory:
    """
    :class:`~nodedge.scene_history.SceneHistory` class

    It contains the code for storing all the previous actions of the user in a dictionary.
    """

    def __init__(self, scene: "Scene", maxLength: int = 32) -> None:  # type: ignore # noqa: F821
        """
        :param scene: reference to the :class:`~nodedge.scene.Scene`
        :type scene: :class:`~nodedge.scene.Scene`
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
        Register the callback associated with a `HistoryModified` event.

        :param callback: callback function
        """
        self._historyModifiedListeners.append(callback)

    def addHistoryStoredListener(self, callback):
        """
        Register the callback associated with a `HistoryStored` event.

        :param callback: callback function
        """
        self._historyStoredListeners.append(callback)

    def addHistoryRestoredListener(self, callback):
        """
        Register the callback associated with a `HistoryRestored` event.

        :param callback: callback function
        """
        self._historyRestoredListeners.append(callback)

    def clear(self, storeInitialStamp=True):
        """
        Reset the history stack.
        """
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
        """
        Helper function usually used when new or open file operations
        are requested.
        """
        self.store("Initial history stamp", sceneIsModified=False)

    @property
    def canUndo(self) -> bool:
        """
        This property returns ``True`` if the undo operation is available for the current history stack.

        :rtype: ``bool``
        """
        return self.currentStep > 0

    @property
    def canRedo(self) -> bool:
        """
        This property returns ``True`` if the redo operation is available for the current history stack.

        :rtype: ``bool``
        """
        return self.currentStep + 1 < len(self.stack)

    def undo(self):
        """
        Perform the undo operation.
        """
        self.__logger.debug("Undo")

        if self.canUndo:
            self.currentStep -= 1
            self.restore()

    def redo(self):
        """
        Perform the redo operation
        """
        self.__logger.debug("Redo")

        if self.canRedo:
            self.currentStep += 1
            self.restore()
            self.scene.isModified = True

    def store(self, desc, sceneIsModified=True):
        """
        Store the history stamp into the history stack.

        :param desc: Description of current history stamp
        :type desc: ``str``
        :param sceneIsModified: if ``True`` marks that :class:`~nodedge.scene.Scene` has been modified
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
        Restore history stamp from history stack.

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
        Create a history stamp.
        Internally it serializes the whole scene and the current selection.

        :param desc: Descriptive label for the history stamp
        :return: history stamp serializing the state of the scene
            and the current selection
        :rtype: ``dict``
        """
        selectedObjects = {"nodes": [], "edges": []}

        for item in self.scene.graphicsScene.selectedItems():
            if hasattr(item, "node"):
                selectedObjects["nodes"].append(item.node.id)
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
        Restore history stamp to the current scene, included indication of the selected items.

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
        except Exception as e:
            self.__logger.warning("Failed to restore stamp")
            dumpException(e)
