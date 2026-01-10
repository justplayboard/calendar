import sys
import os
import winreg

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

from globals import *

form = resource_path("settings.ui")
form_class = uic.loadUiType(form)[0]

class settings(QDialog, form_class):
    APP_NAME = ""

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("설정")
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.APP_NAME = self.getExeName()

        self.checkBox_1.setText("윈도우 시작 시 자동 실행")
        self.checkBox_1.setChecked(self.isStartupEnabled())
        self.checkBox_1.stateChanged.connect(self.toggleStartup)

# ====================================================================================================

    def getExeName(self):
        if getattr(sys, "frozen", False):
            path = sys.executable
        else:
            path = os.path.abspath(__file__)

        baseName = os.path.basename(path)
        name, ext = os.path.splitext(baseName)
        return name
    
    def getExeDir(self):
        if getattr(sys, "frozen", False):
            path = sys.executable
        else:
            path = os.path.abspath(__file__)

        dirName = os.path.dirname(path)
        return dirName

    def getExePath(self):
        if getattr(sys, "frozen", False):
            return sys.executable
        return os.path.abspath(sys.argv[0])
    
    def isStartupEnabled(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            winreg.QueryValueEx(key, self.APP_NAME)
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False

    # 시작프로그램 등록 함수
    def enableStartup(self):
        exePath = self.getExePath()
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key, self.APP_NAME, 0, winreg.REG_SZ, exePath)
        winreg.CloseKey(key)

    # 시작프로그램 삭제 함수
    def disableStartup(self):
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE
            )
            winreg.DeleteValue(key, self.APP_NAME)
            winreg.CloseKey(key)
        except FileNotFoundError:
            pass

    # 시작프로그램 설정 함수
    def toggleStartup(self, state):
        if state:
            self.enableStartup()
        else:
            self.disableStartup()

# ====================================================================================================

    # 버튼 이벤트 함수
    def cntButtonRole(self, button):
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.AcceptRole:
            self.sendMemo()
        elif role == QDialogButtonBox.RejectRole:
            pass

    # 마우스 이벤트 설정
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.mouseClick = True
            self.oldPos = e.globalPos()
    def mouseReleaseEvent(self, e):
        self.mouseClick = False
    def mouseMoveEvent(self, e):
        if self.mouseClick:
            delta = QPoint(e.globalPos() - self.oldPos)
            x = self.x() + delta.x()
            y = self.y() + delta.y()

            desktop = QApplication.desktop()
            currentScreen = desktop.screenNumber(self)
            screenGeo = desktop.availableGeometry(currentScreen)

            if e.globalPos().x() < screenGeo.left() + self.width and e.globalPos().y() < screenGeo.top() + self.height:
                self.move(screenGeo.left(), screenGeo.top())
            elif e.globalPos().x() > screenGeo.right() - self.width and e.globalPos().y() < screenGeo.top() + self.height:
                self.move(screenGeo.right() - self.width, 0)
            elif e.globalPos().x() < screenGeo.left() + self.width and e.globalPos().y() > screenGeo.bottom() - self.height:
                self.move(screenGeo.left(), screenGeo.bottom() - self.height)
            elif e.globalPos().x() > screenGeo.right() - self.width and e.globalPos().y() > screenGeo.bottom() - self.height:
                self.move(screenGeo.right() - self.width, screenGeo.bottom() - self.height)
            elif e.globalPos().y() < screenGeo.top() + self.height:
                self.move(x, screenGeo.top())
            elif e.globalPos().x() < screenGeo.left() + self.width:
                self.move(screenGeo.left(), y)
            elif e.globalPos().x() > screenGeo.right() - self.width:
                self.move(screenGeo.right() - self.width, y)
            elif e.globalPos().y() > screenGeo.bottom() - self.height:
                self.move(x, screenGeo.bottom() - self.height)
            else:
                self.move(x, y)
                
            self.oldPos = e.globalPos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = settings()
    myWindow.show()
    app.exec_()
