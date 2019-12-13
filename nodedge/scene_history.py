import logging
from nodedge.graphics_edge import GraphicsEdge


class SceneHistory:
    def __init__(self, scene, maxLength=32):
        self.scene = scene

        self.__logger = logging.getLogger(__file__)
        self.__logger.setLevel(logging.INFO)

        self.stack = []
        self.currentStep = -1
        self._maxLength = maxLength

    def __str__(self):
        dlog = f"History [{self.currentStep} / {len(self.stack)}, max. {self._maxLength}]"
        for ind, value in enumerate(self.stack):
            dlog += f"\n|||| {ind}: {value['desc']}"

        return dlog

    def undo(self):
        self.__logger.debug("Undo")

        if self.currentStep > 0:
            self.currentStep -= 1
            self.restore()

    def redo(self):
        self.__logger.debug("Redo")

        if self.currentStep+1 < len(self.stack):
            self.currentStep += 1
            self.restore()

    def store(self, desc, sceneHasBeenModified=True):
        self.__logger.debug(f"Storing \'{desc}\' in history with current step: {self.currentStep} / {len(self.stack)} "
                            f"(max. {self._maxLength})")
        stamp = self._createStamp(desc)

        # If the current step is not at the end of the stack.
        if self.currentStep+1 < len(self.stack):
            self.stack = self.stack[0:self.currentStep+1]

        # If history is outside of limits
        if self.currentStep+1 >= self._maxLength:
            self.currentStep -= 1
            self.stack.pop(0)

        self.stack.append(stamp)
        self.currentStep += 1
        self.__logger.debug(f"Setting step to {self.currentStep}")

        self.scene.hasBeenModified = sceneHasBeenModified

    def restore(self):
        self.__logger.debug(f"Restoring history with current step: {self.currentStep} / {len(self.stack)} "
                            f"(max. {self._maxLength})")

        self._restoreStamp(self.stack[self.currentStep])

    def _createStamp(self, desc):
        selectedObjects = {
            "nodes": [],
            "edges": []
        }

        for item in self.scene.graphicsScene.selectedItems():
            if hasattr(item, "node"):
                selectedObjects["nodes"].append(item.node.id)
            elif isinstance(item, GraphicsEdge):
                selectedObjects["edges"].append(item.edge.id)

        stamp = {
            "desc": desc,
            "snapshot": self.scene.serialize(),
            "selection": selectedObjects
        }

        return stamp

    def _restoreStamp(self, stamp):
        self.__logger.debug(f"Restoring stamp: {stamp['selection']}")

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
