# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setEnabled(True)
        MainWindow.resize(550, 470)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMinimumSize(QtCore.QSize(550, 470))
        MainWindow.setMaximumSize(QtCore.QSize(550, 749))
        MainWindow.setStatusTip(_fromUtf8(""))
        MainWindow.setStyleSheet(_fromUtf8(""))
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.btn_batch_start = QtGui.QPushButton(self.centralwidget)
        self.btn_batch_start.setGeometry(QtCore.QRect(10, 710, 431, 31))
        self.btn_batch_start.setObjectName(_fromUtf8("btn_batch_start"))
        self.spinbox_p2 = QtGui.QDoubleSpinBox(self.centralwidget)
        self.spinbox_p2.setGeometry(QtCore.QRect(460, 130, 81, 22))
        self.spinbox_p2.setDecimals(0)
        self.spinbox_p2.setMaximum(3000.0)
        self.spinbox_p2.setSingleStep(25.0)
        self.spinbox_p2.setProperty("value", 1300.0)
        self.spinbox_p2.setObjectName(_fromUtf8("spinbox_p2"))
        self.slider_syringe = QtGui.QSlider(self.centralwidget)
        self.slider_syringe.setGeometry(QtCore.QRect(240, 100, 251, 31))
        self.slider_syringe.setStyleSheet(_fromUtf8("QSlider::groove:horizontal {\n"
"border: 1px solid #999999;\n"
"height: 18px;\n"
"\n"
"border-radius: 9px;\n"
"}\n"
"\n"
"QSlider::handle:horizontal {\n"
"width: 18px;\n"
"}\n"
"\n"
"QSlider::add-page:qlineargradient {\n"
"background: darkgrey;\n"
"border-top-right-radius: 9px;\n"
"border-bottom-right-radius: 9px;\n"
"border-top-left-radius: 0px;\n"
"border-bottom-left-radius: 0px;\n"
"}\n"
"\n"
"QSlider::sub-page:qlineargradient {\n"
"background: lightblue;\n"
"border-top-right-radius: 0px;\n"
"border-bottom-right-radius: 0px;\n"
"border-top-left-radius: 0px;\n"
"border-bottom-left-radius: 0px;\n"
"}"))
        self.slider_syringe.setMaximum(95)
        self.slider_syringe.setPageStep(1)
        self.slider_syringe.setProperty("value", 14)
        self.slider_syringe.setOrientation(QtCore.Qt.Horizontal)
        self.slider_syringe.setInvertedAppearance(True)
        self.slider_syringe.setInvertedControls(False)
        self.slider_syringe.setObjectName(_fromUtf8("slider_syringe"))
        self.spinbox_carbon_current = QtGui.QDoubleSpinBox(self.centralwidget)
        self.spinbox_carbon_current.setGeometry(QtCore.QRect(330, 130, 91, 22))
        self.spinbox_carbon_current.setDecimals(2)
        self.spinbox_carbon_current.setMaximum(5.0)
        self.spinbox_carbon_current.setSingleStep(0.1)
        self.spinbox_carbon_current.setProperty("value", 1.4)
        self.spinbox_carbon_current.setObjectName(_fromUtf8("spinbox_carbon_current"))
        self.btn_hevac_he = QtGui.QPushButton(self.centralwidget)
        self.btn_hevac_he.setGeometry(QtCore.QRect(0, 80, 71, 31))
        self.btn_hevac_he.setCheckable(False)
        self.btn_hevac_he.setObjectName(_fromUtf8("btn_hevac_he"))
        self.btn_hevac_vac = QtGui.QPushButton(self.centralwidget)
        self.btn_hevac_vac.setGeometry(QtCore.QRect(0, 120, 71, 31))
        self.btn_hevac_vac.setCheckable(False)
        self.btn_hevac_vac.setObjectName(_fromUtf8("btn_hevac_vac"))
        self.line_hevac_vac = QtGui.QFrame(self.centralwidget)
        self.line_hevac_vac.setGeometry(QtCore.QRect(70, 120, 81, 31))
        self.line_hevac_vac.setFrameShape(QtGui.QFrame.HLine)
        self.line_hevac_vac.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_hevac_vac.setObjectName(_fromUtf8("line_hevac_vac"))
        self.line_hevac_he = QtGui.QFrame(self.centralwidget)
        self.line_hevac_he.setGeometry(QtCore.QRect(70, 80, 81, 31))
        self.line_hevac_he.setFrameShape(QtGui.QFrame.HLine)
        self.line_hevac_he.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_hevac_he.setObjectName(_fromUtf8("line_hevac_he"))
        self.line_syringe = QtGui.QFrame(self.centralwidget)
        self.line_syringe.setGeometry(QtCore.QRect(220, 90, 20, 51))
        self.line_syringe.setFrameShadow(QtGui.QFrame.Plain)
        self.line_syringe.setFrameShape(QtGui.QFrame.HLine)
        self.line_syringe.setObjectName(_fromUtf8("line_syringe"))
        self.line_4 = QtGui.QFrame(self.centralwidget)
        self.line_4.setGeometry(QtCore.QRect(140, 95, 20, 39))
        self.line_4.setFrameShadow(QtGui.QFrame.Plain)
        self.line_4.setFrameShape(QtGui.QFrame.VLine)
        self.line_4.setObjectName(_fromUtf8("line_4"))
        self.line_5 = QtGui.QFrame(self.centralwidget)
        self.line_5.setGeometry(QtCore.QRect(150, 100, 21, 31))
        self.line_5.setFrameShadow(QtGui.QFrame.Plain)
        self.line_5.setFrameShape(QtGui.QFrame.HLine)
        self.line_5.setObjectName(_fromUtf8("line_5"))
        self.btn_ams = QtGui.QPushButton(self.centralwidget)
        self.btn_ams.setGeometry(QtCore.QRect(175, 20, 40, 35))
        self.btn_ams.setCheckable(False)
        self.btn_ams.setObjectName(_fromUtf8("btn_ams"))
        self.line_ams = QtGui.QFrame(self.centralwidget)
        self.line_ams.setGeometry(QtCore.QRect(180, 0, 31, 21))
        self.line_ams.setFrameShape(QtGui.QFrame.VLine)
        self.line_ams.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_ams.setObjectName(_fromUtf8("line_ams"))
        self.btn_syringe_valve = QtGui.QPushButton(self.centralwidget)
        self.btn_syringe_valve.setGeometry(QtCore.QRect(170, 90, 51, 51))
        self.btn_syringe_valve.setFlat(True)
        self.btn_syringe_valve.setObjectName(_fromUtf8("btn_syringe_valve"))
        self.btn_cracker8 = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker8.setGeometry(QtCore.QRect(10, 290, 51, 141))
        self.btn_cracker8.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_cracker8.setObjectName(_fromUtf8("btn_cracker8"))
        self.btn_cracker7 = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker7.setGeometry(QtCore.QRect(60, 290, 51, 141))
        self.btn_cracker7.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_cracker7.setObjectName(_fromUtf8("btn_cracker7"))
        self.btn_cracker6 = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker6.setGeometry(QtCore.QRect(110, 290, 51, 141))
        self.btn_cracker6.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_cracker6.setObjectName(_fromUtf8("btn_cracker6"))
        self.btn_cracker5 = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker5.setGeometry(QtCore.QRect(160, 290, 51, 141))
        self.btn_cracker5.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_cracker5.setObjectName(_fromUtf8("btn_cracker5"))
        self.btn_cracker3 = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker3.setGeometry(QtCore.QRect(260, 290, 51, 141))
        self.btn_cracker3.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_cracker3.setObjectName(_fromUtf8("btn_cracker3"))
        self.btn_cracker4 = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker4.setGeometry(QtCore.QRect(210, 290, 51, 141))
        self.btn_cracker4.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_cracker4.setObjectName(_fromUtf8("btn_cracker4"))
        self.btn_cracker2 = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker2.setGeometry(QtCore.QRect(310, 290, 51, 141))
        self.btn_cracker2.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_cracker2.setObjectName(_fromUtf8("btn_cracker2"))
        self.btn_cracker1 = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker1.setGeometry(QtCore.QRect(360, 290, 51, 141))
        self.btn_cracker1.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_cracker1.setObjectName(_fromUtf8("btn_cracker1"))
        self.line_v2syringe = QtGui.QFrame(self.centralwidget)
        self.line_v2syringe.setGeometry(QtCore.QRect(170, 140, 51, 61))
        self.line_v2syringe.setFrameShadow(QtGui.QFrame.Plain)
        self.line_v2syringe.setFrameShape(QtGui.QFrame.VLine)
        self.line_v2syringe.setObjectName(_fromUtf8("line_v2syringe"))
        self.btn_v2 = QtGui.QPushButton(self.centralwidget)
        self.btn_v2.setGeometry(QtCore.QRect(175, 200, 40, 35))
        self.btn_v2.setObjectName(_fromUtf8("btn_v2"))
        self.btn_blank = QtGui.QPushButton(self.centralwidget)
        self.btn_blank.setGeometry(QtCore.QRect(440, 290, 51, 141))
        self.btn_blank.setObjectName(_fromUtf8("btn_blank"))
        self.btn_ox = QtGui.QPushButton(self.centralwidget)
        self.btn_ox.setGeometry(QtCore.QRect(490, 290, 51, 141))
        self.btn_ox.setObjectName(_fromUtf8("btn_ox"))
        self.line_cracker1 = QtGui.QFrame(self.centralwidget)
        self.line_cracker1.setGeometry(QtCore.QRect(10, 240, 185, 21))
        self.line_cracker1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_cracker1.setFrameShape(QtGui.QFrame.HLine)
        self.line_cracker1.setObjectName(_fromUtf8("line_cracker1"))
        self.btn_selector_cracker = QtGui.QPushButton(self.centralwidget)
        self.btn_selector_cracker.setGeometry(QtCore.QRect(10, 260, 401, 31))
        self.btn_selector_cracker.setStyleSheet(_fromUtf8(""))
        self.btn_selector_cracker.setFlat(False)
        self.btn_selector_cracker.setObjectName(_fromUtf8("btn_selector_cracker"))
        self.btn_selector_blank = QtGui.QPushButton(self.centralwidget)
        self.btn_selector_blank.setGeometry(QtCore.QRect(440, 260, 51, 31))
        self.btn_selector_blank.setObjectName(_fromUtf8("btn_selector_blank"))
        self.btn_selector_ox = QtGui.QPushButton(self.centralwidget)
        self.btn_selector_ox.setGeometry(QtCore.QRect(490, 260, 51, 31))
        self.btn_selector_ox.setObjectName(_fromUtf8("btn_selector_ox"))
        self.btn_he = QtGui.QPushButton(self.centralwidget)
        self.btn_he.setGeometry(QtCore.QRect(10, 430, 231, 31))
        self.btn_he.setObjectName(_fromUtf8("btn_he"))
        self.btn_pump = QtGui.QPushButton(self.centralwidget)
        self.btn_pump.setGeometry(QtCore.QRect(0, 160, 71, 31))
        self.btn_pump.setCheckable(False)
        self.btn_pump.setAutoDefault(False)
        self.btn_pump.setDefault(False)
        self.btn_pump.setFlat(False)
        self.btn_pump.setObjectName(_fromUtf8("btn_pump"))
        self.line_pump = QtGui.QFrame(self.centralwidget)
        self.line_pump.setGeometry(QtCore.QRect(70, 160, 125, 31))
        self.line_pump.setLineWidth(1)
        self.line_pump.setMidLineWidth(0)
        self.line_pump.setFrameShape(QtGui.QFrame.HLine)
        self.line_pump.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_pump.setObjectName(_fromUtf8("line_pump"))
        self.lcd_p2 = QtGui.QLCDNumber(self.centralwidget)
        self.lcd_p2.setGeometry(QtCore.QRect(480, 30, 61, 23))
        self.lcd_p2.setFrameShape(QtGui.QFrame.Panel)
        self.lcd_p2.setFrameShadow(QtGui.QFrame.Sunken)
        self.lcd_p2.setDigitCount(4)
        self.lcd_p2.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.lcd_p2.setProperty("value", 1300.0)
        self.lcd_p2.setObjectName(_fromUtf8("lcd_p2"))
        self.lcd_p1 = QtGui.QLCDNumber(self.centralwidget)
        self.lcd_p1.setGeometry(QtCore.QRect(410, 30, 61, 23))
        self.lcd_p1.setFrameShape(QtGui.QFrame.Panel)
        self.lcd_p1.setFrameShadow(QtGui.QFrame.Sunken)
        self.lcd_p1.setSmallDecimalPoint(False)
        self.lcd_p1.setDigitCount(4)
        self.lcd_p1.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.lcd_p1.setProperty("value", 1300.0)
        self.lcd_p1.setProperty("intValue", 1300)
        self.lcd_p1.setObjectName(_fromUtf8("lcd_p1"))
        self.btn_start_drive = QtGui.QPushButton(self.centralwidget)
        self.btn_start_drive.setGeometry(QtCore.QRect(240, 80, 41, 21))
        self.btn_start_drive.setCheckable(True)
        self.btn_start_drive.setObjectName(_fromUtf8("btn_start_drive"))
        self.btn_optimize = QtGui.QPushButton(self.centralwidget)
        self.btn_optimize.setGeometry(QtCore.QRect(280, 80, 61, 21))
        self.btn_optimize.setCheckable(True)
        self.btn_optimize.setObjectName(_fromUtf8("btn_optimize"))
        self.btn_cracker_open = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker_open.setGeometry(QtCore.QRect(240, 430, 41, 31))
        self.btn_cracker_open.setCheckable(True)
        self.btn_cracker_open.setObjectName(_fromUtf8("btn_cracker_open"))
        self.btn_cracker_crack = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker_crack.setGeometry(QtCore.QRect(280, 430, 41, 31))
        self.btn_cracker_crack.setObjectName(_fromUtf8("btn_cracker_crack"))
        self.btn_batch_stop = QtGui.QPushButton(self.centralwidget)
        self.btn_batch_stop.setGeometry(QtCore.QRect(490, 710, 51, 31))
        self.btn_batch_stop.setObjectName(_fromUtf8("btn_batch_stop"))
        self.list_batch_list = QtGui.QListWidget(self.centralwidget)
        self.list_batch_list.setGeometry(QtCore.QRect(390, 470, 151, 231))
        self.list_batch_list.setVerticalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.list_batch_list.setHorizontalScrollMode(QtGui.QAbstractItemView.ScrollPerPixel)
        self.list_batch_list.setFlow(QtGui.QListView.LeftToRight)
        self.list_batch_list.setProperty("isWrapping", True)
        self.list_batch_list.setLayoutMode(QtGui.QListView.SinglePass)
        self.list_batch_list.setViewMode(QtGui.QListView.ListMode)
        self.list_batch_list.setObjectName(_fromUtf8("list_batch_list"))
        item = QtGui.QListWidgetItem()
        self.list_batch_list.addItem(item)
        self.txtedit_batch_in = QtGui.QTextEdit(self.centralwidget)
        self.txtedit_batch_in.setEnabled(True)
        self.txtedit_batch_in.setGeometry(QtCore.QRect(10, 470, 371, 201))
        self.txtedit_batch_in.setAutoFormatting(QtGui.QTextEdit.AutoBulletList)
        self.txtedit_batch_in.setObjectName(_fromUtf8("txtedit_batch_in"))
        self.btn_view = QtGui.QPushButton(self.centralwidget)
        self.btn_view.setGeometry(QtCore.QRect(0, 0, 71, 21))
        self.btn_view.setCheckable(True)
        self.btn_view.setObjectName(_fromUtf8("btn_view"))
        self.line_10 = QtGui.QFrame(self.centralwidget)
        self.line_10.setGeometry(QtCore.QRect(180, 55, 31, 36))
        self.line_10.setFrameShadow(QtGui.QFrame.Plain)
        self.line_10.setFrameShape(QtGui.QFrame.VLine)
        self.line_10.setObjectName(_fromUtf8("line_10"))
        self.line_11 = QtGui.QFrame(self.centralwidget)
        self.line_11.setGeometry(QtCore.QRect(180, 235, 31, 15))
        self.line_11.setFrameShadow(QtGui.QFrame.Plain)
        self.line_11.setFrameShape(QtGui.QFrame.VLine)
        self.line_11.setObjectName(_fromUtf8("line_11"))
        self.lineedit_execute = QtGui.QLineEdit(self.centralwidget)
        self.lineedit_execute.setGeometry(QtCore.QRect(10, 680, 301, 21))
        self.lineedit_execute.setObjectName(_fromUtf8("lineedit_execute"))
        self.line_cracker2 = QtGui.QFrame(self.centralwidget)
        self.line_cracker2.setGeometry(QtCore.QRect(195, 240, 215, 21))
        self.line_cracker2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_cracker2.setFrameShape(QtGui.QFrame.HLine)
        self.line_cracker2.setObjectName(_fromUtf8("line_cracker2"))
        self.line_bottles1 = QtGui.QFrame(self.centralwidget)
        self.line_bottles1.setGeometry(QtCore.QRect(410, 240, 81, 21))
        self.line_bottles1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_bottles1.setFrameShape(QtGui.QFrame.HLine)
        self.line_bottles1.setObjectName(_fromUtf8("line_bottles1"))
        self.btn_offset = QtGui.QPushButton(self.centralwidget)
        self.btn_offset.setGeometry(QtCore.QRect(390, 80, 81, 21))
        self.btn_offset.setObjectName(_fromUtf8("btn_offset"))
        self.btn_transfer_blank = QtGui.QPushButton(self.centralwidget)
        self.btn_transfer_blank.setGeometry(QtCore.QRect(440, 430, 51, 31))
        self.btn_transfer_blank.setObjectName(_fromUtf8("btn_transfer_blank"))
        self.btn_transfer_ox = QtGui.QPushButton(self.centralwidget)
        self.btn_transfer_ox.setGeometry(QtCore.QRect(490, 430, 51, 31))
        self.btn_transfer_ox.setObjectName(_fromUtf8("btn_transfer_ox"))
        self.lcd_m2 = QtGui.QLCDNumber(self.centralwidget)
        self.lcd_m2.setGeometry(QtCore.QRect(360, 30, 41, 23))
        self.lcd_m2.setFrameShape(QtGui.QFrame.Panel)
        self.lcd_m2.setFrameShadow(QtGui.QFrame.Sunken)
        self.lcd_m2.setDigitCount(3)
        self.lcd_m2.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.lcd_m2.setProperty("value", 12.0)
        self.lcd_m2.setProperty("intValue", 12)
        self.lcd_m2.setObjectName(_fromUtf8("lcd_m2"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(360, 10, 41, 20))
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(410, 10, 61, 20))
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.lcd_mixture = QtGui.QLCDNumber(self.centralwidget)
        self.lcd_mixture.setGeometry(QtCore.QRect(310, 30, 41, 23))
        self.lcd_mixture.setFrameShape(QtGui.QFrame.Panel)
        self.lcd_mixture.setFrameShadow(QtGui.QFrame.Sunken)
        self.lcd_mixture.setSmallDecimalPoint(True)
        self.lcd_mixture.setDigitCount(3)
        self.lcd_mixture.setSegmentStyle(QtGui.QLCDNumber.Flat)
        self.lcd_mixture.setProperty("value", 5.0)
        self.lcd_mixture.setProperty("intValue", 5)
        self.lcd_mixture.setObjectName(_fromUtf8("lcd_mixture"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(310, 10, 41, 20))
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.lbl_working = QtGui.QLabel(self.centralwidget)
        self.lbl_working.setGeometry(QtCore.QRect(230, 220, 311, 20))
        self.lbl_working.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_working.setObjectName(_fromUtf8("lbl_working"))
        self.btn_clean = QtGui.QPushButton(self.centralwidget)
        self.btn_clean.setGeometry(QtCore.QRect(350, 80, 41, 21))
        self.btn_clean.setObjectName(_fromUtf8("btn_clean"))
        self.line_bottles2 = QtGui.QFrame(self.centralwidget)
        self.line_bottles2.setGeometry(QtCore.QRect(490, 240, 51, 21))
        self.line_bottles2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_bottles2.setFrameShape(QtGui.QFrame.HLine)
        self.line_bottles2.setObjectName(_fromUtf8("line_bottles2"))
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(420, 130, 41, 20))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.label_5 = QtGui.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(480, 10, 61, 20))
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.lbl_pos = QtGui.QLabel(self.centralwidget)
        self.lbl_pos.setGeometry(QtCore.QRect(500, 105, 41, 21))
        self.lbl_pos.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lbl_pos.setObjectName(_fromUtf8("lbl_pos"))
        self.btn_cracker_crack_transfer = QtGui.QPushButton(self.centralwidget)
        self.btn_cracker_crack_transfer.setGeometry(QtCore.QRect(320, 430, 91, 31))
        self.btn_cracker_crack_transfer.setObjectName(_fromUtf8("btn_cracker_crack_transfer"))
        self.chk_in_position = QtGui.QCheckBox(self.centralwidget)
        self.chk_in_position.setGeometry(QtCore.QRect(10, 230, 111, 17))
        self.chk_in_position.setObjectName(_fromUtf8("chk_in_position"))
        self.btn_execute = QtGui.QPushButton(self.centralwidget)
        self.btn_execute.setGeometry(QtCore.QRect(320, 680, 61, 21))
        self.btn_execute.setCheckable(False)
        self.btn_execute.setObjectName(_fromUtf8("btn_execute"))
        self.btn_batch_next = QtGui.QPushButton(self.centralwidget)
        self.btn_batch_next.setGeometry(QtCore.QRect(440, 710, 51, 31))
        self.btn_batch_next.setObjectName(_fromUtf8("btn_batch_next"))
        self.btn_clear_plot = QtGui.QPushButton(self.centralwidget)
        self.btn_clear_plot.setGeometry(QtCore.QRect(70, 20, 71, 21))
        self.btn_clear_plot.setObjectName(_fromUtf8("btn_clear_plot"))
        self.btn_mix_blank = QtGui.QPushButton(self.centralwidget)
        self.btn_mix_blank.setGeometry(QtCore.QRect(222, 30, 41, 21))
        self.btn_mix_blank.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_mix_blank.setFlat(True)
        self.btn_mix_blank.setObjectName(_fromUtf8("btn_mix_blank"))
        self.btn_mix_ox = QtGui.QPushButton(self.centralwidget)
        self.btn_mix_ox.setGeometry(QtCore.QRect(262, 30, 41, 21))
        self.btn_mix_ox.setStyleSheet(_fromUtf8("background-color: #dfdfdf; border: 1px solid #999999;"))
        self.btn_mix_ox.setFlat(True)
        self.btn_mix_ox.setObjectName(_fromUtf8("btn_mix_ox"))
        self.btn_save_data = QtGui.QPushButton(self.centralwidget)
        self.btn_save_data.setGeometry(QtCore.QRect(0, 20, 71, 21))
        self.btn_save_data.setObjectName(_fromUtf8("btn_save_data"))
        self.chk_kickstart = QtGui.QCheckBox(self.centralwidget)
        self.chk_kickstart.setGeometry(QtCore.QRect(240, 130, 61, 21))
        self.chk_kickstart.setChecked(True)
        self.chk_kickstart.setObjectName(_fromUtf8("chk_kickstart"))
        self.spinbox_min_slope = QtGui.QDoubleSpinBox(self.centralwidget)
        self.spinbox_min_slope.setGeometry(QtCore.QRect(480, 160, 61, 21))
        self.spinbox_min_slope.setDecimals(2)
        self.spinbox_min_slope.setMaximum(5.0)
        self.spinbox_min_slope.setSingleStep(0.01)
        self.spinbox_min_slope.setProperty("value", 0.15)
        self.spinbox_min_slope.setObjectName(_fromUtf8("spinbox_min_slope"))
        self.label_6 = QtGui.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(340, 160, 131, 20))
        self.label_6.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.btn_fc_offset = QtGui.QPushButton(self.centralwidget)
        self.btn_fc_offset.setGeometry(QtCore.QRect(470, 80, 71, 21))
        self.btn_fc_offset.setCheckable(True)
        self.btn_fc_offset.setObjectName(_fromUtf8("btn_fc_offset"))
        self.btn_plot_ratios = QtGui.QPushButton(self.centralwidget)
        self.btn_plot_ratios.setGeometry(QtCore.QRect(70, 0, 71, 21))
        self.btn_plot_ratios.setCheckable(True)
        self.btn_plot_ratios.setObjectName(_fromUtf8("btn_plot_ratios"))
        self.btn_attach_window = QtGui.QPushButton(self.centralwidget)
        self.btn_attach_window.setGeometry(QtCore.QRect(0, 40, 141, 16))
        self.btn_attach_window.setCheckable(True)
        self.btn_attach_window.setObjectName(_fromUtf8("btn_attach_window"))
        self.label_7 = QtGui.QLabel(self.centralwidget)
        self.label_7.setGeometry(QtCore.QRect(227, 10, 71, 20))
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.spinbox_min_error = QtGui.QDoubleSpinBox(self.centralwidget)
        self.spinbox_min_error.setGeometry(QtCore.QRect(480, 190, 61, 21))
        self.spinbox_min_error.setDecimals(2)
        self.spinbox_min_error.setMaximum(5.0)
        self.spinbox_min_error.setSingleStep(0.01)
        self.spinbox_min_error.setProperty("value", 0.0)
        self.spinbox_min_error.setObjectName(_fromUtf8("spinbox_min_error"))
        self.label_8 = QtGui.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(340, 190, 131, 20))
        self.label_8.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.btn_batch_start.raise_()
        self.spinbox_p2.raise_()
        self.slider_syringe.raise_()
        self.spinbox_carbon_current.raise_()
        self.line_hevac_vac.raise_()
        self.line_hevac_he.raise_()
        self.btn_hevac_he.raise_()
        self.btn_hevac_vac.raise_()
        self.line_4.raise_()
        self.line_5.raise_()
        self.line_ams.raise_()
        self.btn_ams.raise_()
        self.btn_syringe_valve.raise_()
        self.btn_cracker8.raise_()
        self.btn_cracker7.raise_()
        self.btn_cracker6.raise_()
        self.btn_cracker5.raise_()
        self.btn_cracker3.raise_()
        self.btn_cracker4.raise_()
        self.btn_cracker2.raise_()
        self.btn_cracker1.raise_()
        self.btn_blank.raise_()
        self.btn_ox.raise_()
        self.btn_selector_cracker.raise_()
        self.btn_selector_blank.raise_()
        self.btn_selector_ox.raise_()
        self.btn_he.raise_()
        self.line_pump.raise_()
        self.btn_pump.raise_()
        self.line_cracker1.raise_()
        self.btn_v2.raise_()
        self.lcd_p2.raise_()
        self.lcd_p1.raise_()
        self.btn_start_drive.raise_()
        self.btn_optimize.raise_()
        self.btn_cracker_open.raise_()
        self.btn_cracker_crack.raise_()
        self.btn_batch_stop.raise_()
        self.list_batch_list.raise_()
        self.txtedit_batch_in.raise_()
        self.btn_view.raise_()
        self.line_syringe.raise_()
        self.line_v2syringe.raise_()
        self.line_10.raise_()
        self.line_11.raise_()
        self.lineedit_execute.raise_()
        self.line_cracker2.raise_()
        self.line_bottles1.raise_()
        self.btn_offset.raise_()
        self.btn_transfer_blank.raise_()
        self.btn_transfer_ox.raise_()
        self.lcd_m2.raise_()
        self.label.raise_()
        self.label_2.raise_()
        self.lcd_mixture.raise_()
        self.label_3.raise_()
        self.lbl_working.raise_()
        self.btn_clean.raise_()
        self.line_bottles2.raise_()
        self.label_4.raise_()
        self.label_5.raise_()
        self.lbl_pos.raise_()
        self.btn_cracker_crack_transfer.raise_()
        self.chk_in_position.raise_()
        self.btn_execute.raise_()
        self.btn_batch_next.raise_()
        self.btn_clear_plot.raise_()
        self.btn_mix_blank.raise_()
        self.btn_mix_ox.raise_()
        self.btn_save_data.raise_()
        self.chk_kickstart.raise_()
        self.spinbox_min_slope.raise_()
        self.label_6.raise_()
        self.btn_fc_offset.raise_()
        self.btn_plot_ratios.raise_()
        self.btn_attach_window.raise_()
        self.label_7.raise_()
        self.spinbox_min_error.raise_()
        self.label_8.raise_()
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Gas Injection System - Current Efficiency: 7.4%  | Time to go: 723 s", None))
        self.btn_batch_start.setText(_translate("MainWindow", "Start Batch", None))
        self.spinbox_p2.setSuffix(_translate("MainWindow", " mbar", None))
        self.spinbox_carbon_current.setSuffix(_translate("MainWindow", " mug/min", None))
        self.btn_hevac_he.setText(_translate("MainWindow", "He", None))
        self.btn_hevac_vac.setText(_translate("MainWindow", "Pump", None))
        self.btn_ams.setText(_translate("MainWindow", "AMS", None))
        self.btn_syringe_valve.setText(_translate("MainWindow", "/", None))
        self.btn_cracker8.setText(_translate("MainWindow", "8", None))
        self.btn_cracker7.setText(_translate("MainWindow", "7", None))
        self.btn_cracker6.setText(_translate("MainWindow", "6", None))
        self.btn_cracker5.setText(_translate("MainWindow", "5", None))
        self.btn_cracker3.setText(_translate("MainWindow", "3", None))
        self.btn_cracker4.setText(_translate("MainWindow", "4", None))
        self.btn_cracker2.setText(_translate("MainWindow", "2", None))
        self.btn_cracker1.setText(_translate("MainWindow", "1", None))
        self.btn_v2.setText(_translate("MainWindow", "valve", None))
        self.btn_blank.setText(_translate("MainWindow", "Blank", None))
        self.btn_ox.setText(_translate("MainWindow", "Ox-II", None))
        self.btn_selector_cracker.setText(_translate("MainWindow", "Cracker", None))
        self.btn_selector_blank.setText(_translate("MainWindow", "valve", None))
        self.btn_selector_ox.setText(_translate("MainWindow", "valve", None))
        self.btn_he.setText(_translate("MainWindow", "He", None))
        self.btn_pump.setText(_translate("MainWindow", "Pump", None))
        self.btn_start_drive.setText(_translate("MainWindow", "Drive", None))
        self.btn_optimize.setText(_translate("MainWindow", "Optimize", None))
        self.btn_cracker_open.setText(_translate("MainWindow", "Open", None))
        self.btn_cracker_crack.setText(_translate("MainWindow", "Crack", None))
        self.btn_batch_stop.setText(_translate("MainWindow", "Stop", None))
        __sortingEnabled = self.list_batch_list.isSortingEnabled()
        self.list_batch_list.setSortingEnabled(False)
        item = self.list_batch_list.item(0)
        item.setText(_translate("MainWindow", "# batch list", None))
        self.list_batch_list.setSortingEnabled(__sortingEnabled)
        self.txtedit_batch_in.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\"># batch input</span></p></body></html>", None))
        self.btn_view.setText(_translate("MainWindow", "show batch", None))
        self.lineedit_execute.setPlaceholderText(_translate("MainWindow", "terminal commands here, e.g. transferOx(targetMixture=5.), etc.", None))
        self.btn_offset.setText(_translate("MainWindow", "P1/P2 offset", None))
        self.btn_transfer_blank.setText(_translate("MainWindow", "Transfer", None))
        self.btn_transfer_ox.setText(_translate("MainWindow", "Transfer", None))
        self.label.setText(_translate("MainWindow", "µg", None))
        self.label_2.setText(_translate("MainWindow", "cracker", None))
        self.label_3.setText(_translate("MainWindow", "mixture", None))
        self.lbl_working.setText(_translate("MainWindow", "working..", None))
        self.btn_clean.setText(_translate("MainWindow", "clean", None))
        self.label_4.setText(_translate("MainWindow", "<-->", None))
        self.label_5.setText(_translate("MainWindow", "syringe", None))
        self.lbl_pos.setText(_translate("MainWindow", "31 mm", None))
        self.btn_cracker_crack_transfer.setText(_translate("MainWindow", "Crack + Transfer", None))
        self.chk_in_position.setText(_translate("MainWindow", "cracker in position", None))
        self.btn_execute.setText(_translate("MainWindow", "Execute", None))
        self.btn_batch_next.setText(_translate("MainWindow", "Next >", None))
        self.btn_clear_plot.setText(_translate("MainWindow", "clear plot", None))
        self.btn_mix_blank.setText(_translate("MainWindow", "blank", None))
        self.btn_mix_ox.setText(_translate("MainWindow", "ox-ii", None))
        self.btn_save_data.setText(_translate("MainWindow", "save data", None))
        self.chk_kickstart.setText(_translate("MainWindow", "kickstart", None))
        self.spinbox_min_slope.setSuffix(_translate("MainWindow", " %", None))
        self.label_6.setText(_translate("MainWindow", "min. slope for next opt.:", None))
        self.btn_fc_offset.setText(_translate("MainWindow", "FC offset", None))
        self.btn_plot_ratios.setText(_translate("MainWindow", "plot ratios", None))
        self.btn_attach_window.setText(_translate("MainWindow", "<-- attach plot window", None))
        self.label_7.setText(_translate("MainWindow", "set ratio", None))
        self.spinbox_min_error.setSuffix(_translate("MainWindow", " %", None))
        self.label_8.setText(_translate("MainWindow", "next when error smaller:", None))

