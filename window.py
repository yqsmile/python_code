# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'window.ui',
# licensing of 'window.ui' applies.
#
# Created: Wed Dec  4 11:44:51 2019
#      by: pyside2-uic  running on PySide2 5.13.2
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QFileDialog, QMainWindow, QApplication
from PySide2.QtCore import Slot
import sys
import os
from os.path import isfile, join, isdir, splitext
from os import listdir
from PySide2.QtCore import QThreadPool
from concurrent.futures import ThreadPoolExecutor
from convNC2TXT import conv_nc2txt


class Ui_Form(QtWidgets.QWidget):
    select = QtCore.Signal(int)
    def __init__(self):
        super(Ui_Form,self).__init__()
        self.pool = QThreadPool()
        self.pool.setMaxThreadCount(5)

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(502, 421)
        self.btnInputDir = QtWidgets.QPushButton(Form)
        self.btnInputDir.setGeometry(QtCore.QRect(350, 40, 75, 23))
        self.btnInputDir.setObjectName("inputFile")
        self.txtInputDir = QtWidgets.QLineEdit(Form)
        self.txtInputDir.setGeometry(QtCore.QRect(60, 29, 271, 31))
        self.txtInputDir.setObjectName("inputFilename")
        self.txtOutputDir = QtWidgets.QLineEdit(Form)
        self.txtOutputDir.setGeometry(QtCore.QRect(60, 70, 271, 31))
        self.txtOutputDir.setObjectName("txtOutputDir")
        self.showLog = QtWidgets.QPlainTextEdit(Form)
        self.showLog.setGeometry(QtCore.QRect(10, 240, 481, 181))
        self.showLog.setObjectName("showLog")
        self.btnOutputDir = QtWidgets.QPushButton(Form)
        self.btnOutputDir.setGeometry(QtCore.QRect(350, 70, 75, 23))
        self.btnOutputDir.setObjectName("outputDir")
        self.btnConvert = QtWidgets.QPushButton(Form)
        self.btnConvert.setGeometry(QtCore.QRect(160, 130, 81, 31))
        self.btnConvert.setObjectName("convert")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.btnInputDir.clicked.connect(self.selectInputDir)
        self.btnOutputDir.clicked.connect(self.selectOutputDir)
        self.connect(self, QtCore.SIGNAL('select(int)'), self, QtCore.SLOT('selectDir(int)'))
        self.btnConvert.clicked.connect(self.convertBtnOnClick)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtWidgets.QApplication.translate("Form", "Form", None, -1))
        self.btnInputDir.setText(QtWidgets.QApplication.translate("Form", "inputFile", None, -1))
        self.txtInputDir.setPlaceholderText(QtWidgets.QApplication.translate("Form", "input directory", None, -1))
        self.txtOutputDir.setPlaceholderText(QtWidgets.QApplication.translate("Form", "output directory", None, -1))
        self.btnOutputDir.setText(QtWidgets.QApplication.translate("Form", "outputDir", None, -1))
        self.btnConvert.setText(QtWidgets.QApplication.translate("Form", "convert", None, -1))

    @Slot(QtWidgets.QLineEdit)
    def selectDir(self, tag):
        dir = QFileDialog.getExistingDirectory(self, "open directory", "",
                                               QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if tag == 1:
            self.txtInputDir.setText(dir)
        if tag == 2:
            self.txtOutputDir.setText(dir)

    @Slot()
    def selectInputDir(self):
        self.select.emit(1)

    @Slot()
    def selectOutputDir(self):
        self.select.emit(2)

    @Slot()
    def convertBtnOnClick(self):
        argInputDir = self.txtInputDir.text()
        argOutputDir = self.txtOutputDir.text()
        if argInputDir!='' and argOutputDir!='':
            self.btnConvert.setEnabled(False)
            self.convert(argInputDir,argOutputDir)

    def convert(self,inputDir, outputDir):
        if isdir(inputDir) and isdir(outputDir):
            filenames = [f for f in listdir(inputDir) if isfile(join(inputDir, f)) and splitext(f)[1] == '.nc']
            processors = [convThread(join(inputDir,f),join(outputDir,splitext(f)[0])) for f in filenames]
            for i in processors:
                i.objConnection.finish.connect(self.display)
                self.pool.start(i)
            self.btnConvert.setEnabled(True)

    @Slot(str)
    def display(self,str):
        self.showLog.appendPlainText(str)

class convThread(QtCore.QRunnable):
    def __init__(self,inputFile,outputFile):
        super(convThread,self).__init__()
        self.inputFile = inputFile
        self.outputFile = outputFile
        self.objConnection = ConvConnection()

    def run(self):
        conv_nc2txt(self.inputFile,self.outputFile)
        self.objConnection.finish.emit(self.inputFile+" finish")

class ConvConnection(QtCore.QObject):
    finish = QtCore.Signal(str)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    Mainwindwo = QMainWindow()
    ui = Ui_Form()
    ui.setupUi(Mainwindwo)
    Mainwindwo.show()
    sys.exit(app.exec_())
