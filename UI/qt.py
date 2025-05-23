from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2250, 900)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton_Up = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_Up.setGeometry(QtCore.QRect(1310, 750, 78, 23))
        self.pushButton_Up.setObjectName("pushButton_Up")
        self.submit_llm = QtWidgets.QPushButton(self.centralwidget)
        self.submit_llm.setGeometry(QtCore.QRect(610, 810, 101, 31))
        self.submit_llm.setObjectName("submit_llm")
        self.pushButton_Left = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_Left.setGeometry(QtCore.QRect(1410, 750, 78, 23))
        self.pushButton_Left.setObjectName("pushButton_Left")
        self.pushButton_Down = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_Down.setGeometry(QtCore.QRect(1310, 780, 78, 23))
        self.pushButton_Down.setObjectName("pushButton_Down")
        self.pushButton_Right = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_Right.setGeometry(QtCore.QRect(1410, 780, 78, 23))
        self.pushButton_Right.setObjectName("pushButton_Right")
        self.pushButton_ZoomIn = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_ZoomIn.setGeometry(QtCore.QRect(1310, 810, 78, 23))
        self.pushButton_ZoomIn.setObjectName("pushButton_ZoomIn")
        self.pushButton_ZoomOut = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_ZoomOut.setGeometry(QtCore.QRect(1410, 810, 78, 23))
        self.pushButton_ZoomOut.setObjectName("pushButton_ZoomOut")
        self.show_widget = QtWidgets.QWidget(self.centralwidget)
        self.show_widget.setGeometry(QtCore.QRect(10, 10, 640, 360))
        self.show_widget.setObjectName("show_widget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 520, 721, 261))
        self.textBrowser.setObjectName("textBrowser")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(13, 790, 561, 64))
        self.textEdit.setObjectName("textEdit")
        self.graph_view = QtWidgets.QLabel(self.centralwidget)
        self.graph_view.setGeometry(QtCore.QRect(740, 10, 640, 360))
        self.graph_view.setText("")
        self.graph_view.setObjectName("graph_view")
        # Add new 640x360 widget on the right side of graph_view
        self.additional_widget = QtWidgets.QLabel(self.centralwidget)
        self.additional_widget.setGeometry(QtCore.QRect(1390, 10, 640, 360))
        self.additional_widget.setText("")
        self.additional_widget.setObjectName("additional_widget")

        self.pushButton_screenshot = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_screenshot.setGeometry(QtCore.QRect(1310, 710, 78, 23))
        self.pushButton_screenshot.setObjectName("pushButton_screenshot")
        self.basefind_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.basefind_radioButton.setGeometry(QtCore.QRect(960, 710, 101, 21))
        self.basefind_radioButton.setObjectName("basefind_radioButton")
        self.agentfind_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.agentfind_radioButton.setGeometry(QtCore.QRect(1130, 710, 101, 21))
        self.agentfind_radioButton.setObjectName("agentfind_radioButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(1370, 670, 101, 31))
        self.label.setObjectName("label")
        self.baseallfind_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.baseallfind_radioButton.setGeometry(QtCore.QRect(960, 760, 101, 21))
        self.baseallfind_radioButton.setObjectName("baseallfind_radioButton")
        self.agentallfind_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.agentallfind_radioButton.setGeometry(QtCore.QRect(1130, 760, 101, 21))
        self.agentallfind_radioButton.setObjectName("agentallfind_radioButton")
        self.agentmode_radioButton = QtWidgets.QRadioButton(self.centralwidget)
        self.agentmode_radioButton.setGeometry(QtCore.QRect(1040, 820, 101, 21))
        self.agentmode_radioButton.setObjectName("agentmode_radioButton")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(1060, 670, 101, 31))
        self.label_3.setObjectName("label_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1500, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton_Up.setText(_translate("MainWindow", "向上"))
        self.submit_llm.setText(_translate("MainWindow", "任务提交"))
        self.pushButton_Left.setText(_translate("MainWindow", "向左"))
        self.pushButton_Down.setText(_translate("MainWindow", "向下"))
        self.pushButton_Right.setText(_translate("MainWindow", "向右"))
        self.pushButton_ZoomIn.setText(_translate("MainWindow", "变焦变大"))
        self.pushButton_ZoomOut.setText(_translate("MainWindow", "变焦变小"))
        self.pushButton_screenshot.setText(_translate("MainWindow", "截图"))
        self.basefind_radioButton.setText(_translate("MainWindow", "基本寻物"))
        self.agentfind_radioButton.setText(_translate("MainWindow", "智能寻物"))
        self.label.setText(_translate("MainWindow", "基本功能"))
        self.baseallfind_radioButton.setText(_translate("MainWindow", "基本巡视"))
        self.agentallfind_radioButton.setText(_translate("MainWindow", "智能巡视"))
        self.agentmode_radioButton.setText(_translate("MainWindow", "智能体模式"))
        self.label_3.setText(_translate("MainWindow", "进阶功能"))
