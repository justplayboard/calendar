import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

from globals import *

form = resource_path("editMemo.ui")
form_class = uic.loadUiType(form)[0]

class editMemo(QDialog, form_class):
    signalToMain = pyqtSignal(dict)
    signalToMain_2 = pyqtSignal(dict)

    width = 400
    height = 300

    def __init__(self, msg):
        super().__init__()
        self.setupUi(self)
        # self.setWindowTitle("메모 수정")
        self.setFixedSize(self.width, self.height)
        self.setWindowFlags(Qt.WindowCloseButtonHint)

        self.msg = msg

        self.setWindowTitle(f"{self.msg["year"]}/{self.msg["month"]}/{self.msg["day"]}")

        self.groupBox.setTitle("편집")
        self.textEdit.setText(self.msg["memo"])

        self.pushButton.setText("Delete")
        self.pushButton.clicked.connect(self.deleteMemo)

        self.buttonBox.clicked.connect(self.cntButtonRole)

    @pyqtSlot()
    def deleteMemo(self):
        self.signalToMain_2.emit(self.msg)
        self.close()

    @pyqtSlot()
    def sendMemo(self):
        self.msg["memo"] = self.textEdit.toPlainText()
        self.signalToMain.emit(self.msg)

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
    myWindow = editMemo()
    myWindow.show()
    app.exec_()
