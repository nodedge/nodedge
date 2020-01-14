import logging

from nodedge.graphics_edge import GraphicsEdge
from nodedge.utils import dumpException


class SceneHistory:
    def __init__(self, scene, maxLength=32):
        self.scene = scene

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self._historyModifiedListeners = []

        self._maxLength = maxLength
        self.currentStep = -1
        self.stack = []

    def addHistoryModifiedListener(self, callback):
        self._historyModifiedListeners.append(callback)

    def clear(self, storeInitialStamp=True):
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
        self.store("Initial history stamp")

    @property
    def canUndo(self):
        return self.currentStep > 0

    @property
    def canRedo(self):
        return self.currentStep + 1 < len(self.stack)

    def undo(self):
        self.__logger.debug("Undo")

        if self.canUndo:
            self.currentStep -= 1
            self.restore()
            self.scene.isModified = True

    def redo(self):
        self.__logger.debug("Redo")

        if self.canRedo:
            self.currentStep += 1
            self.restore()
            self.scene.isModified = True

    def store(self, desc, sceneIsModified=True):
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

    def restore(self):
        self.__logger.debug(
            f"Restoring history with current step: {self.currentStep} / {len(self.stack)} "
            f"(max. {self._maxLength})"
        )

        self._restoreStamp(self.stack[self.currentStep])

        for callback in self._historyModifiedListeners:
            callback()

    def _createStamp(self, desc):
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
