import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import uic

import calendar
from datetime import date
import json

from globals import *
from editMemo import *

from widgets.memoBrowser import *

form = resource_path("main.ui")
form_class = uic.loadUiType(form)[0]

class main(QMainWindow, form_class):
    dataLocation = os.getcwd()

    userValues = "userValues.json"

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("캘린더")
        self.setWindowFlags(Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.readUserValues()

        self.setGeometry(self.jsonData["geometry"]["x"], self.jsonData["geometry"]["y"], self.jsonData["geometry"]["width"], self.jsonData["geometry"]["height"])

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        self.verticalLayout = QVBoxLayout(centralWidget)
        self.horizontalLayout = QHBoxLayout()
        self.grid = QGridLayout()
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.addLayout(self.grid)

        today = date.today()
        calendar.setfirstweekday(6)

        box = QGroupBox()
        hLayout = QHBoxLayout()
        box.setLayout(hLayout)
        self.yearBox = QComboBox()
        self.monthBox = QComboBox()

        for i in range(1970, 2101):
            self.yearBox.addItem(str(i))
        for i in range(1, 13):
            self.monthBox.addItem(str(i))

        self.yearBox.setCurrentText(str(today.year))
        self.monthBox.setCurrentText(str(today.month))
        self.yearBox.currentTextChanged.connect(self.showCalendar)
        self.monthBox.currentTextChanged.connect(self.showCalendar)

        leftWidget = QWidget()
        rightWidget = QWidget()

        hLayout.addWidget(leftWidget)
        hLayout.addWidget(self.yearBox)
        hLayout.addWidget(self.monthBox)
        hLayout.addWidget(rightWidget)
        hLayout.setStretch(0, 2)
        hLayout.setStretch(1, 1)
        hLayout.setStretch(2, 1)
        hLayout.setStretch(3, 2)

        leftButton = QPushButton("<", self)
        rightButton = QPushButton(">", self)
        leftButton.clicked.connect(self.downMonth)
        rightButton.clicked.connect(self.upMonth)

        self.horizontalLayout.addWidget(leftButton)
        self.horizontalLayout.addWidget(box)
        self.horizontalLayout.addWidget(rightButton)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 5)
        self.horizontalLayout.setStretch(2, 1)

        self.showCalendar()

    def upMonth(self):
        currentMonth = int(self.monthBox.currentText())
        currentYear = int(self.yearBox.currentText())
        if currentMonth == 12:
            currentYear += 1
            currentMonth = 1
            self.yearBox.setCurrentText(str(currentYear))
            self.monthBox.setCurrentText(str(currentMonth))
        else:
            self.monthBox.setCurrentText(str(currentMonth+1))

    def downMonth(self):
        currentMonth = int(self.monthBox.currentText())
        currentYear = int(self.yearBox.currentText())
        if currentMonth == 1:
            currentYear -= 1
            currentMonth = 12
            self.yearBox.setCurrentText(str(currentYear))
            self.monthBox.setCurrentText(str(currentMonth))
        else:
            self.monthBox.setCurrentText(str(currentMonth-1))

    def readUserValues(self):
        with open(resource_path(self.userValues), 'r', encoding="utf-8") as f:
            self.jsonData = json.load(f)
        filePath = os.path.join(self.dataLocation, self.userValues)
        if not os.path.exists(filePath):
            pass
        else:
            with open(filePath, "r", encoding="utf-8") as f:
                self.jsonData = json.load(f)

    def writeUserValues(self):
        filePath = os.path.join(self.dataLocation, self.userValues)
        with open(filePath, "w", encoding="utf-8") as f:
            json.dump(self.jsonData, f, indent="\t", ensure_ascii=False)

    def isJsonDayKey(self, year, month, day):
        try:
            tmp = self.jsonData["memo"][year][month][day]
        except KeyError:
            return False
        return True
    
    def isJsonMonthKey(self, year, month):
        try:
            tmp = self.jsonData["memo"][year][month]
        except KeyError:
            return False
        return True
    
    def isJsonYearKey(self, year):
        try:
            tmp = self.jsonData["memo"][year]
        except KeyError:
            return False
        return True

    def showEditMemo(self, year, month, day):
        def innerShowEditMemo():
            msg = {
                "memo": self.jsonData["memo"][year][month][day] if self.isJsonDayKey(year, month, day) else "",
                "year": year,
                "month": month,
                "day": day,
            }
            self.editMemo = editMemo(msg=msg)
            self.editMemo.signalToMain.connect(self.setMemo)
            self.editMemo.signalToMain_2.connect(self.removeMemo)
            self.editMemo.show()
            self.editMemo.exec_()
        return innerShowEditMemo

    @pyqtSlot(dict)
    def setMemo(self, msg):
        if self.isJsonYearKey(msg["year"]):
            if self.isJsonMonthKey(msg["year"], msg["month"]):
                if self.isJsonDayKey(msg["year"], msg["month"], msg["day"]):
                    self.jsonData["memo"][msg["year"]][msg["month"]][msg["day"]] = msg["memo"]
                else:
                    newMemo = {
                        msg["day"]: msg["memo"]
                    }
                    self.jsonData["memo"][msg["year"]][msg["month"]].update(newMemo)
            else:
                newMemo = {
                    msg["month"]: {
                        msg["day"]: msg["memo"]
                    }
                }
                self.jsonData["memo"][msg["year"]].update(newMemo)
        else:
            newMemo = {
                msg["year"]: {
                    msg["month"]: {
                        msg["day"]: msg["memo"]
                    }
                }
            }
            self.jsonData["memo"].update(newMemo)

        self.showCalendar()
        self.writeUserValues()

    def showCalendar(self):
        for i in reversed(range(self.grid.count())):
            self.grid.itemAt(i).widget().deleteLater()

        year = self.yearBox.currentText()
        month = self.monthBox.currentText()

        cal = calendar.month(int(year), int(month))
        calList = list(map(str, cal.split("\n")))
        for i, l in enumerate(calList):
            if i == 0:
                yearMonth = l.strip()
                calList[i] = list(map(str, yearMonth.split()))
            else:
                calList[i] = list(map(str, l.split()))

        for i in range(len(calList)-1):
            cnt = len(calList[i+1])
            for j in range(cnt):
                day = calList[i+1][j]

                if i == 0:
                    browser = QTextBrowser()
                    browser.setFixedHeight(25)
                    browser.append(day)
                else:
                    memo = self.jsonData["memo"][year][month][day] if self.isJsonDayKey(year, month, day) else ""
                    browser = memoBrowser()
                    browser.signalToMain.connect(self.showEditMemo(year, month, day))
                    browser.append(day)
                    browser.append("")
                    browser.append(memo)
                if i == 1:
                    self.grid.addWidget(browser, i, 7-cnt)
                    cnt -= 1
                else:
                    self.grid.addWidget(browser, i, j)

    @pyqtSlot(dict)
    def removeMemo(self, msg):
        if self.isJsonDayKey(msg["year"], msg["month"], msg["day"]):
            del self.jsonData["memo"][msg["year"]][msg["month"]][msg["day"]]
            self.showCalendar()
            self.writeUserValues()

# ====================================================================================================

    # esc 끄기
    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, e):
        self.jsonData["geometry"]["x"] = self.geometry().x()
        self.jsonData["geometry"]["y"] = self.geometry().y()
        self.jsonData["geometry"]["width"] = self.geometry().width()
        self.jsonData["geometry"]["height"] = self.geometry().height()
        self.writeUserValues()
        app.quit()

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

            if e.globalPos().x() < screenGeo.left() + self.frameGeometry().width() and e.globalPos().y() < screenGeo.top() + self.frameGeometry().height():
                self.jsonData["geometry"]["x"] = screenGeo.left()
                self.jsonData["geometry"]["y"] = screenGeo.top()
            elif e.globalPos().x() > screenGeo.right() - self.frameGeometry().width() and e.globalPos().y() < screenGeo.top() + self.frameGeometry().height():
                self.jsonData["geometry"]["x"] = screenGeo.right() - self.frameGeometry().width()
                self.jsonData["geometry"]["y"] = 0
            elif e.globalPos().x() < screenGeo.left() + self.frameGeometry().width() and e.globalPos().y() > screenGeo.bottom() - self.frameGeometry().height():
                self.jsonData["geometry"]["x"] = screenGeo.left()
                self.jsonData["geometry"]["y"] = screenGeo.bottom() - self.frameGeometry().height()
            elif e.globalPos().x() > screenGeo.right() - self.frameGeometry().width() and e.globalPos().y() > screenGeo.bottom() - self.frameGeometry().height():
                self.jsonData["geometry"]["x"] = screenGeo.right() - self.frameGeometry().width()
                self.jsonData["geometry"]["y"] = screenGeo.bottom() - self.frameGeometry().height()
            elif e.globalPos().y() < screenGeo.top() + self.frameGeometry().height():
                self.jsonData["geometry"]["x"] = x
                self.jsonData["geometry"]["y"] = screenGeo.top()
            elif e.globalPos().x() < screenGeo.left() + self.frameGeometry().width():
                self.jsonData["geometry"]["x"] = screenGeo.left()
                self.jsonData["geometry"]["y"] = y
            elif e.globalPos().x() > screenGeo.right() - self.frameGeometry().width():
                self.jsonData["geometry"]["x"] = screenGeo.right() - self.frameGeometry().width()
                self.jsonData["geometry"]["y"] = y
            elif e.globalPos().y() > screenGeo.bottom() - self.frameGeometry().height():
                self.jsonData["geometry"]["x"] = x
                self.jsonData["geometry"]["y"] = screenGeo.bottom() - self.frameGeometry().height()
            else:
                self.jsonData["geometry"]["x"] = x
                self.jsonData["geometry"]["y"] = y
                
            self.oldPos = e.globalPos()

            # self.move(self.jsonData["geometry"]["x"], self.jsonData["geometry"]["y"])
            self.writeUserValues()

# ====================================================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = main()
    myWindow.show()
    app.exec_()
