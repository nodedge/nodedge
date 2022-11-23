from PySide6.QtCore import QCoreApplication


class GraphicsSplashScreen(object):
    def __init__(self):
        self.labelLoading = None
        self.labelCredits = None
        self.progressBar = None
        self.labelDescription = None
        self.labelTitle = None
        self.dropShadowFrame = None
        self.verticalLayout = None
        self.centralWidget = None

    def setupUi(self, SplashScreen):
        if not SplashScreen.objectName():
            SplashScreen.setObjectName("SplashScreen")

    def translateUi(self, SplashScreen):
        SplashScreen.setWindowTitle(
            QCoreApplication.translate("SplashScreen", "MainWindow", None)
        )
        self.labelTitle.setText(
            QCoreApplication.translate(
                "SplashScreen", "<html><head/><body><p>NODEDGE</p></body></html>", None
            )
        )
        self.labelDescription.setText(
            QCoreApplication.translate(
                "SplashScreen",
                "<html><head/><body><p>FOR NEXT-GENERATION SCIENTIFIC PROGRAMMING</p></body></html>",
                None,
            )
        )
        self.labelLoading.setText(
            QCoreApplication.translate(
                "SplashScreen", "<strong>Loading</strong> ...", None
            )
        )
        self.labelCredits.setText(
            QCoreApplication.translate(
                "SplashScreen",
                "<html><head/><body><p>Copyright (c) 2020-2022 Nodedge Foundation</p></body></html>",
                None,
            )
        )
