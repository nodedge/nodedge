from collections import OrderedDict
from typing import Optional

from nodedge.serializable import Serializable


class SolverConfiguration:
    def __init__(self):
        self.solver = None
        self.solverName = None
        self.solverOptions = None
        self.timeStep = None
        self.maxIterations = None
        self.tolerance = None

    def to_dict(self):
        return {
            "solver": self.solver,
            "solverName": self.solverName,
            "solverOptions": self.solverOptions,
            "timeStep": self.timeStep,
            "maxIterations": self.maxIterations,
            "tolerance": self.tolerance,
        }

    def from_dict(self, data: dict) -> bool:
        self.solver = data["solver"]
        self.solverName = data["solverName"]
        self.solverOptions = data["solverOptions"]
        self.timeStep = data["timeStep"]
        self.maxIterations = data["maxIterations"]
        self.tolerance = data["tolerance"]

        return True


class SceneSimulator(Serializable):
    def __init__(self, scene: "Scene"):  # type: ignore
        super().__init__()
        self.config = SolverConfiguration()
        self.scene: "Scene" = scene  # type: ignore

    def run(self):
        pass

    def serialize(self):
        return OrderedDict(self.config.to_dict())

    def deserialize(
        self,
        data: dict,
        hashmap: Optional[dict] = None,
        restoreId: bool = True,
        *args,
        **kwargs,
    ) -> bool:
        self.config = SolverConfiguration()
        deserializationValidity = self.config.from_dict(data)

        return deserializationValidity

    def updateConfig(self, config: SolverConfiguration):
        self.config = config
