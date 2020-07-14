# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ScheduleUI/beastScheduleUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtWidgets

class Ui_Form(object): #DONE Namenänderung und Einbinden von Wahrscheinlichkeit und Länge des Wasserzufuhr
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(502, 372)
        self.gridLayout = QtWidgets.QGridLayout(Form)
        self.gridLayout.setObjectName("gridLayout")
        self.label_5 = QtWidgets.QLabel(Form)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 8, 4, 1, 2)
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 11, 0, 1, 2)
        self.line = QtWidgets.QFrame(Form)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 3, 0, 1, 9)
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 10, 0, 1, 9)
        self.pretrainingCheck = QtWidgets.QRadioButton(Form)
        self.pretrainingCheck.setText("")
        self.pretrainingCheck.setObjectName("pretrainingCheck")
        self.gridLayout.addWidget(self.pretrainingCheck, 9, 0, 1, 2)
        self.label_9 = QtWidgets.QLabel(Form)
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 8, 0, 1, 2)
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 2)
#        self.label_4 = QtWidgets.QLabel(Form)
#        self.label_4.setObjectName("label_4")
#        self.gridLayout.addWidget(self.label_4, 4, 2, 1, 2)
        self.trialOffsetEdit = QtWidgets.QLineEdit(Form)
        self.trialOffsetEdit.setObjectName("trialOffsetEdit")
        self.gridLayout.addWidget(self.trialOffsetEdit, 9, 6, 1, 2)
        self.label_6 = QtWidgets.QLabel(Form)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 8, 6, 1, 2)
        self.nTrialsEdit = QtWidgets.QLineEdit(Form)
        self.nTrialsEdit.setObjectName("nTrialsEdit")
        self.gridLayout.addWidget(self.nTrialsEdit, 7, 0, 1, 2)
#        self.trialLengthEdit = QtWidgets.QLineEdit(Form)
#        self.trialLengthEdit.setObjectName("trialLengthEdit")
#        self.gridLayout.addWidget(self.trialLengthEdit, 7, 2, 1, 2)
        self.nValveSpin = QtWidgets.QSpinBox(Form)
        self.nValveSpin.setMinimum(1)
        self.nValveSpin.setMaximum(3)
        self.nValveSpin.setProperty("value", 3)
        self.nValveSpin.setObjectName("nValveSpin")
        self.gridLayout.addWidget(self.nValveSpin, 11, 8, 1, 1)
        self.label_12 = QtWidgets.QLabel(Form)
        self.label_12.setObjectName("label_12")
        self.gridLayout.addWidget(self.label_12, 11, 5, 1, 3)
        
        #reward map table
        self.rewardMapTable = QtWidgets.QTableWidget(Form)
        self.rewardMapTable.setToolTipDuration(-1)
        self.rewardMapTable.setColumnCount(3)
        self.rewardMapTable.setMinimumHeight(200)
        self.rewardMapTable.setObjectName("rewardMapTable")
        self.rewardMapTable.setRowCount(2)
        
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setVerticalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setVerticalHeaderItem(1, item)
        
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setHorizontalHeaderItem(2, item)
        
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setItem(0, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setItem(0, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setItem(0, 2, item)
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setItem(1, 0, item)
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setItem(1, 1, item)
        item = QtWidgets.QTableWidgetItem()
        self.rewardMapTable.setItem(1, 2, item)
        
        self.rewardMapTable.horizontalHeader().setCascadingSectionResizes(False)
        self.rewardMapTable.horizontalHeader().setDefaultSectionSize(35)
        self.rewardMapTable.horizontalHeader().setStretchLastSection(False)
        self.gridLayout.addWidget(self.rewardMapTable, 12, 0, 1, 9)
        
        self.label = QtWidgets.QLabel(Form)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 4)
        
        self.label_15 = QtWidgets.QLabel(Form)
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 1, 6, 1, 2, QtCore.Qt.AlignTop)
        self.trialOnsetEdit = QtWidgets.QLineEdit(Form)
        self.trialOnsetEdit.setObjectName("trialOnsetEdit")
        self.gridLayout.addWidget(self.trialOnsetEdit, 9, 4, 1, 2)
        self.lickFractionEdit = QtWidgets.QLineEdit(Form)
        self.lickFractionEdit.setObjectName("lickFractionEdit")
        self.gridLayout.addWidget(self.lickFractionEdit, 9, 8, 1, 1)
        self.label_10 = QtWidgets.QLabel(Form)
        self.label_10.setObjectName("label_10")
        self.gridLayout.addWidget(self.label_10, 8, 8, 1, 1)
#        self.label_13 = QtWidgets.QLabel(Form)
#        self.label_13.setObjectName("label_13")
#        self.gridLayout.addWidget(self.label_13, 8, 2, 1, 1)
#        self.waitTrainingCheck = QtWidgets.QRadioButton(Form)
#        self.waitTrainingCheck.setText("")
#        self.waitTrainingCheck.setObjectName("waitTrainingCheck")
#        self.gridLayout.addWidget(self.waitTrainingCheck, 9, 2, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_5.setText(_translate("Form", "Trial Onset (s)"))
        self.label_7.setText(_translate("Form", "Reward Map:"))
        self.label_9.setText(_translate("Form", "Pretraining"))
        self.label_3.setText(_translate("Form", "Number of Trials"))
#        self.label_4.setText(_translate("Form", "Odor (s)"))
        self.trialOffsetEdit.setText(_translate("Form", "0.05"))
        self.label_6.setText(_translate("Form", "Trial Offset (s)"))
        self.nTrialsEdit.setText(_translate("Form", "100"))
#        self.trialLengthEdit.setText(_translate("Form", "2.0"))
        self.label_12.setText(_translate("Form", "<html><head/><body><p align=\"right\">Number of odours:</p></body></html>"))
        self.rewardMapTable.setToolTip(_translate("Form", "<html><head/><body><p>the columns represent the odours</p></body></html>"))
        item = self.rewardMapTable.verticalHeaderItem(0)
        item.setText(_translate("Form", "Trial Length (s)"))
        item = self.rewardMapTable.verticalHeaderItem(1)
        item.setText(_translate("Form", "Reward Amount (s)"))
        
        item = self.rewardMapTable.horizontalHeaderItem(0)
        item.setText(_translate("Form", "1"))
        item = self.rewardMapTable.horizontalHeaderItem(1)
        item.setText(_translate("Form", "2"))
        item = self.rewardMapTable.horizontalHeaderItem(2)
        item.setText(_translate("Form", "3"))
        __sortingEnabled = self.rewardMapTable.isSortingEnabled()
        self.rewardMapTable.setSortingEnabled(False)
        item = self.rewardMapTable.item(0, 0)
        item.setText(_translate("Form", "2.0"))
        item = self.rewardMapTable.item(1, 0)
        item.setText(_translate("Form", "0.2"))
        item = self.rewardMapTable.item(0, 1)
        item.setText(_translate("Form", "2.0"))
        item = self.rewardMapTable.item(1, 1)
        item.setText(_translate("Form", "0.5"))
        item = self.rewardMapTable.item(0, 2)
        item.setText(_translate("Form", "2.0"))
        item = self.rewardMapTable.item(1, 2)
        item.setText(_translate("Form", "0.8"))
        self.rewardMapTable.setSortingEnabled(__sortingEnabled)
        self.label.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:14pt;\">Autonomouse 2 - Schedule</span></p></body></html>"))
#        self.label_2.setText(_translate("Form", "<html><head/><body><p>Valve Map : <br/>0 = blank <br/>1 = odour 1 <br/>2 = odour 2<br/>3 = odour 3 <br/></p></body></html>"))
        #self.label_2.setText(_translate("Form", "Delay (s)"))
        self.label_15.setText(_translate("Form",""))
#        self.label_15.setText(_translate("Form", "\n"
#"4 = odour 4\n"
#"5 = odour 5\n"
#"6 = odour 6\n"
#"7 = odour 7"))
        self.trialOnsetEdit.setText(_translate("Form", "0.05"))
#        self.label_8.setText(_translate("Form", "Reverse Valence"))
        self.lickFractionEdit.setText(_translate("Form", "0.1"))
        self.label_10.setText(_translate("Form", "Lick Fraction"))
#        self.label_13.setText(_translate("Form", "Wait Training"))

