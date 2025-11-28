import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class memoBrowser(QTextBrowser):
    signalToMain = pyqtSignal()

    @pyqtSlot()
    def mouseDoubleClickEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.signalToMain.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = memoBrowser()
    myWindow.show()
    app.exec_()
