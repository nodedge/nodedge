from PySide6.QtCore import QSettings

DEFAULT_WORKSPACE = "~/Nodedge"


class NodedgeSettings:
    def __init__(self):
        self.workspacePath = ""
        self.theme = ""


class NodedgeSettingsManager:
    def __init__(self):
        self.applicationName: str = "Nodedge"
        self.companyName: str = "Nodedge"

        self.settings = NodedgeSettings()

    def readSettings(self) -> None:
        """
        Read the permanent profile settings for this application.
        """
        if self.applicationName == "":
            return

        settings = QSettings(self.companyName, self.applicationName)
        # self.restoreGeometry(settings.value("windowGeometry"))  # type: ignore
        # self.debugMode = settings.value("debug", False)
        self.settings.workspacePath = settings.value("workspacePath", DEFAULT_WORKSPACE)

    def writeSettings(self) -> None:
        """
        Write the permanent profile settings for this application.
        """
        if self.applicationName is "":
            return

        settings = QSettings(self.companyName, self.applicationName)
        # settings.setValue("debug", self.debugMode)
        # settings.setValue("windowGeometry", self.saveGeometry())
        settings.setValue("workspacePath", self.settings.workspacePath)

    def updateSettings(self, settings: NodedgeSettings):
        self.settings = settings
