# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Splash_screenaYdWoQ.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QLabel, QMainWindow, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_SplashScreen(object):
    def setupUi(self, SplashScreen):
        if not SplashScreen.objectName():
            SplashScreen.setObjectName(u"SplashScreen")
        SplashScreen.resize(600, 400)
        SplashScreen.setStyleSheet(u"background: black;")
        self.centralwidget = QWidget(SplashScreen)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splashscreen_img = QLabel(self.centralwidget)
        self.splashscreen_img.setObjectName(u"splashscreen_img")
        self.splashscreen_img.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout.addWidget(self.splashscreen_img)

        self.please_wait_label = QLabel(self.centralwidget)
        self.please_wait_label.setObjectName(u"please_wait_label")
        font = QFont()
        font.setPointSize(16)
        self.please_wait_label.setFont(font)
        self.please_wait_label.setStyleSheet(u"color: red;")

        self.verticalLayout.addWidget(self.please_wait_label)

        SplashScreen.setCentralWidget(self.centralwidget)

        self.retranslateUi(SplashScreen)

        QMetaObject.connectSlotsByName(SplashScreen)
    # setupUi

    def retranslateUi(self, SplashScreen):
        SplashScreen.setWindowTitle(QCoreApplication.translate("SplashScreen", u"SplashScreen", None))
        self.splashscreen_img.setText("")
        self.please_wait_label.setText(QCoreApplication.translate("SplashScreen", u"Please Wait ...", None))
    # retranslateUi

