from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, Qt)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QFrame, QLabel, QProgressBar, QVBoxLayout, QWidget)


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
            SplashScreen.setObjectName(u"SplashScreen")
        SplashScreen.resize(680, 400)
        self.centralWidget = QWidget(SplashScreen)
        self.centralWidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.dropShadowFrame = QFrame(self.centralWidget)
        self.dropShadowFrame.setObjectName(u"dropShadowFrame")
        self.dropShadowFrame.setStyleSheet(u"QFrame {	\n"
                                           "	background-color: #23252E;	\n"
                                           "	color: #272C36;\n"
                                           "	border-radius: 10px;\n"
                                           "}")
        self.dropShadowFrame.setFrameShape(QFrame.StyledPanel)
        self.dropShadowFrame.setFrameShadow(QFrame.Raised)
        self.labelTitle = QLabel(self.dropShadowFrame)
        self.labelTitle.setObjectName(u"label_title")
        self.labelTitle.setGeometry(QRect(0, 90, 661, 61))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(40)
        self.labelTitle.setFont(font)
        self.labelTitle.setStyleSheet(u"color: #007BFF;")
        self.labelTitle.setAlignment(Qt.AlignCenter)
        self.labelDescription = QLabel(self.dropShadowFrame)
        self.labelDescription.setObjectName(u"label_description")
        self.labelDescription.setGeometry(QRect(0, 150, 661, 61))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(14)
        self.labelDescription.setFont(font1)
        self.labelDescription.setStyleSheet(u"color: rgb(75, 80, 99);")
        self.labelDescription.setAlignment(Qt.AlignCenter)
        self.progressBar = QProgressBar(self.dropShadowFrame)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setGeometry(QRect(50, 280, 561, 23))
        self.progressBar.setStyleSheet(u"QProgressBar {\n"
                                       "	\n"
                                       "	background-color: rgb(75, 80, 99);\n"
                                       "	color: rgb(200, 200, 200);\n"
                                       "	border-style: none;\n"
                                       "	border-radius: 10px;\n"
                                       "	text-align: center;\n"
                                       "}\n"
                                       "QProgressBar::chunk{\n"
                                       "	border-radius: 10px;\n"
                                       "	background-color: qlineargradient(spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523, stop:0 rgba(251, 255, 0, 255), stop:1 rgba(255, 150, 0, 255));\n"
                                       "}")
        self.progressBar.setValue(24)
        self.labelLoading = QLabel(self.dropShadowFrame)
        self.labelLoading.setObjectName(u"label_loading")
        self.labelLoading.setGeometry(QRect(0, 320, 661, 21))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(12)
        self.labelLoading.setFont(font2)
        self.labelLoading.setStyleSheet(u"color: rgb(75, 80, 99);")
        self.labelLoading.setAlignment(Qt.AlignCenter)
        self.labelCredits = QLabel(self.dropShadowFrame)
        self.labelCredits.setObjectName(u"label_credits")
        self.labelCredits.setGeometry(QRect(20, 350, 621, 21))
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(10)
        self.labelCredits.setFont(font3)
        self.labelCredits.setStyleSheet(u"color: rgb(75, 80, 99);")
        self.labelCredits.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.verticalLayout.addWidget(self.dropShadowFrame)
        SplashScreen.setCentralWidget(self.centralWidget)
        self.translateUi(SplashScreen)
        QMetaObject.connectSlotsByName(SplashScreen)

    def translateUi(self, SplashScreen):
        SplashScreen.setWindowTitle(QCoreApplication.translate("SplashScreen", u"MainWindow", None))
        self.labelTitle.setText(
            QCoreApplication.translate("SplashScreen", u"<html><head/><body><p>NODEDGE</p></body></html>", None))
        self.labelDescription.setText(QCoreApplication.translate("SplashScreen",
                                                                  u"<html><head/><body><p>FOR NEXT-GENERATION SCIENTIFIC PROGRAMMING</p></body></html>",
                                                                 None))
        self.labelLoading.setText(QCoreApplication.translate("SplashScreen", u"<strong>Loading</strong> ...", None))
        self.labelCredits.setText(QCoreApplication.translate("SplashScreen",
                                                              u"<html><head/><body><p>Copyright (c) 2020-2022 Nodedge Foundation</p></body></html>",
                                                             None))
