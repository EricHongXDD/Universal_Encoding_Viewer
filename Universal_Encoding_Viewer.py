# -*- coding: utf-8 -*-
import res.image
import webbrowser
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QWidget

from MessageBox import Ui_Form_MessageBox
from Decode_Choose import Ui_Form_Decode
from Encode_Choose import Ui_Form_Encode
from Convert_Choose import Ui_Form_Convert
from analyze_gpt import analyze_gpt

# GPT线程类
class GptThread(QThread):
    # 更新推测数据的信号量
    string_signal = pyqtSignal(str)

    def __init__(self, ui_form_instance):
        super(GptThread, self).__init__()
        # 保存对Ui_Form实例的引用
        self.ui_form_instance = ui_form_instance
        self.running = True

    def run(self):
        # 获取文本前64个字节用于预测
        with open(self.ui_form_instance.open_file_path, 'rb') as file:
            # 读取前64个字节
            bytes_data = file.read(64)
        # 将每个字节转换为16进制，并用空格隔开
        hex_data = ' '.join(f'{byte:02x}' for byte in bytes_data)
        # 获取参数
        API_KEY = self.ui_form_instance.lineEdit.text()
        API_URL = self.ui_form_instance.lineEdit_2.text()
        PROXY = self.ui_form_instance.lineEdit_3.text()
        MODEL = self.ui_form_instance.lineEdit_4.text()
        # 开始预测
        analyze_result = analyze_gpt(API_KEY, API_URL, PROXY, MODEL, hex_data)
        # 发出信号
        self.string_signal.emit(analyze_result)

#消息提示窗口
class Ui_MessageBox(QWidget, Ui_Form_MessageBox):
    def __init__(self, text=""):
        super().__init__()
        self.setupUi(self)
        #设置传入的text
        self.label_20.setText(text)
        # 设置无边框
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # 设置主背景透明
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

#编码查看表格
class HexModel(QtCore.QAbstractTableModel):
    def __init__(self, data, character_encoding='utf-8', parent=None):
        super(HexModel, self).__init__(parent)
        self._data = data
        self.character_encoding = character_encoding

    def rowCount(self, parent=None):
        return (len(self._data) + 15) // 16

    def columnCount(self, parent=None):
        return 17  # 16 columns for hex values, 1 for the text representation

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            byte_index = index.row() * 16 + index.column()
            if index.column() < 16:  # 十六进制表示
                if byte_index < len(self._data):  # 确保不超出数据范围
                    return '{:02X}'.format(self._data[byte_index])
                else:
                    return ""  # 数据不满16字节的部分用空字符串填充
            else:  # 文本表示
                if index.column() == 16:  # 只在最后一列处理文本
                    start = index.row() * 16
                    end = min(start + 16, len(self._data))
                    bytes_slice = self._data[start:end]
                    try:
                        # 解码整个字节切片
                        decoded_text = bytes_slice.decode(self.character_encoding, errors='strict')
                        # 用点填充无法显示的字符
                        printable_text = ''.join(c if c.isprintable() else '·' for c in decoded_text)
                        return printable_text
                    except UnicodeDecodeError as e:
                        # 如果在行的中间遇到解码错误，尝试解码直到出错的部分
                        valid_text = bytes_slice[:e.start].decode(self.character_encoding, errors='strict')
                        # 用点填充解码错误后的剩余部分
                        return valid_text + '·' * (16 - len(valid_text))
                    # except LookupError:
                    #     print("编码错误")
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                if section < 16:
                    return '{:X}'.format(section)
                else:
                    return 'Text'
            else:
                return '{:010X}'.format(section * 16)

#查看其它编码窗口
class Ui_Decode(QWidget, Ui_Form_Decode):
    def __init__(self, ui_form_instance):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 保存对Ui_Form实例的引用
        self.ui_form_instance = ui_form_instance

        # 连接pushButton_11的点击事件，确保只连接一次
        self.pushButton_11.clicked.disconnect()
        # 连接pushButton_11的点击事件
        self.pushButton_11.clicked.connect(self.on_pushButton_11_clicked)
        # # 连接pushButton_4的点击事件，确保只连接一次
        # self.pushButton_4.clicked.disconnect()
        # # 连接pushButton_4的点击事件
        # self.pushButton_4.clicked.connect(self.on_pushButton_4_clicked)

    def on_pushButton_11_clicked(self):
        # 获取lineEdit_4的内容
        text = self.lineEdit_4.text()
        # 检查输入的编码格式是否有效
        if self.ui_form_instance.is_valid_encoding(text) == True:
            # 调用Ui_Form的decode方法，并传递lineEdit_4的内容
            self.ui_form_instance.decode(text)
        else:
            self.ui_form_instance.showMessageBox("编码格式："+text+" 暂不支持")

    # def on_pushButton_4_clicked(self):
    #     # 将tabWidget_2的Tab移到首位置，防止其它不变了
    #     self.ui_form_instance.tabWidget_2.setCurrentIndex(0)
    #     # 关闭当前窗口
    #     self.close()

#其它转换其它编码窗口
class Ui_Encode(QWidget, Ui_Form_Encode):
    def __init__(self, ui_form_instance):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 保存对Ui_Form实例的引用
        self.ui_form_instance = ui_form_instance

        # 连接pushButton_15的点击事件，确保只连接一次
        self.pushButton_15.clicked.disconnect()
        # 连接pushButton_15的点击事件
        self.pushButton_15.clicked.connect(self.on_pushButton_15_clicked)
        # 连接pushButton_4的点击事件，确保只连接一次
        self.pushButton_4.clicked.disconnect()
        # 连接pushButton_4的点击事件
        self.pushButton_4.clicked.connect(self.on_pushButton_4_clicked)


    def on_pushButton_15_clicked(self):
        # 获取原编码格式character_encoding, 获取新编码格式character_decoding
        character_encoding = self.lineEdit_4.text()
        character_decoding = self.lineEdit_5.text()
        # 检查输入的原编码格式是否有效
        if self.ui_form_instance.is_valid_encoding(character_encoding) == True:
            # 检查输入的新编码格式是否有效
            if self.ui_form_instance.is_valid_encoding(character_decoding) == True:
                # 调用Ui_Form的convert_and_save_file方法
                self.ui_form_instance.convert_and_save_file(character_encoding, character_decoding)
            else:
                self.ui_form_instance.showMessageBox("新编码格式：" + character_decoding + " 暂不支持")
        else:
            self.ui_form_instance.showMessageBox("原编码格式："+character_encoding+" 暂不支持")

    def on_pushButton_4_clicked(self):
        # 将tabWidget_3的Tab移到首位置，防止其它转其它出现
        self.ui_form_instance.tabWidget_3.setCurrentIndex(0)
        # 关闭当前窗口
        self.close()

#已有编码转换其它编码窗口
class Ui_Convert(QWidget, Ui_Form_Convert):
    def __init__(self, ui_form_instance):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # 保存对Ui_Form实例的引用
        self.ui_form_instance = ui_form_instance

        # 连接pushButton_11的点击事件，确保只连接一次
        self.pushButton_11.clicked.disconnect()
        # 连接pushButton_11的点击事件
        self.pushButton_11.clicked.connect(self.on_pushButton_11_clicked)

    def on_pushButton_11_clicked(self):
        # 获取原编码格式character_encoding, 获取新编码格式character_decoding
        character_encoding = self.ui_form_instance.tabWidget_3.tabText(self.ui_form_instance.tabWidget_3.currentIndex())
        character_decoding = self.lineEdit_4.text()
        # 检查输入的编码格式是否有效
        if self.ui_form_instance.is_valid_encoding(character_decoding) == True:
            # 调用Ui_Form的convert_and_save_file方法
            self.ui_form_instance.convert_and_save_file(character_encoding, character_decoding)
        else:
            self.ui_form_instance.showMessageBox("编码格式："+character_decoding+" 暂不支持")

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(960, 535)
        Form.setStyleSheet("font-family: 57 12pt \"Alibaba PuHuiTi\";")
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(170, 70, 721, 401))
        self.tabWidget.setStyleSheet("QTabWidget::pane{\n"
"min-width:70px;\n"
"min-height:25px;\n"
"border-top: 1px solid;\n"
"border-color: white;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"\n"
"min-width:150px;\n"
"\n"
"min-height:25px;\n"
"\n"
"color: white;\n"
"\n"
"font: 57 12pt \"Alibaba PuHuiTi\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"\n"
"\n"
"}\n"
"\n"
"QTabBar::tab:selected{\n"
"\n"
"min-width:150px;\n"
"\n"
"min-height:25px;\n"
"color: white;\n"
"\n"
"font: 57 13pt \"Alibaba PuHuiTi\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"border-bottom: 4px solid;\n"
"\n"
"border-color: #4796f0;\n"
"\n"
"}\n"
"")
        self.tabWidget.setObjectName("tabWidget")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.tabWidget_2 = QtWidgets.QTabWidget(self.tab_1)
        self.tabWidget_2.setGeometry(QtCore.QRect(0, 10, 661, 31))
        self.tabWidget_2.setStyleSheet("QTabWidget::pane{\n"
"min-width:70px;\n"
"min-height:25px;\n"
"border-top: 1px solid;\n"
"border-color: white;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"\n"
"min-width:94.4px;\n"
"\n"
"min-height:25px;\n"
"\n"
"color: white;\n"
"\n"
"font: 57 12pt \"Alibaba PuHuiTi\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"\n"
"\n"
"}\n"
"\n"
"QTabBar::tab:selected{\n"
"\n"
"min-width:94.4px;\n"
"\n"
"min-height:25px;\n"
"color: white;\n"
"\n"
"font: 57 13pt \"Alibaba PuHuiTi\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"border-bottom: 5px solid;\n"
"\n"
"border-color: #4796f0;\n"
"\n"
"}\n"
"")
        self.tabWidget_2.setObjectName("tabWidget_2")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget_2.addTab(self.tab_3, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.tabWidget_2.addTab(self.tab_4, "")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.tabWidget_2.addTab(self.tab_6, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget_2.addTab(self.tab, "")
        self.tab_7 = QtWidgets.QWidget()
        self.tab_7.setObjectName("tab_7")
        self.tabWidget_2.addTab(self.tab_7, "")
        self.tab_8 = QtWidgets.QWidget()
        self.tab_8.setObjectName("tab_8")
        self.tabWidget_2.addTab(self.tab_8, "")
        self.tab_15 = QtWidgets.QWidget()
        self.tab_15.setObjectName("tab_15")
        self.tabWidget_2.addTab(self.tab_15, "")
        self.tableView = QtWidgets.QTableView(self.tab_1)
        self.tableView.setGeometry(QtCore.QRect(0, 40, 661, 331))
        self.tableView.setStyleSheet("font: 75 9pt \"Alibaba PuHuiTi\";")
        self.tableView.setObjectName("tableView")
        self.label_8 = QtWidgets.QLabel(self.tab_1)
        self.label_8.setGeometry(QtCore.QRect(20, 40, 61, 31))
        self.label_8.setStyleSheet("color: black;\n"
"font: 57 12pt \"Alibaba PuHuiTi\";")
        self.label_8.setObjectName("label_8")
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget_3 = QtWidgets.QTabWidget(self.tab_2)
        self.tabWidget_3.setGeometry(QtCore.QRect(0, 10, 661, 31))
        self.tabWidget_3.setStyleSheet("QTabWidget::pane{\n"
"min-width:70px;\n"
"min-height:25px;\n"
"border-top: 1px solid;\n"
"border-color: white;\n"
"}\n"
"\n"
"QTabBar::tab {\n"
"\n"
"min-width:94.4px;\n"
"\n"
"min-height:25px;\n"
"\n"
"color: white;\n"
"\n"
"font: 57 12pt \"Alibaba PuHuiTi\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"\n"
"\n"
"}\n"
"\n"
"QTabBar::tab:selected{\n"
"\n"
"min-width:94.4px;\n"
"\n"
"min-height:25px;\n"
"color: white;\n"
"\n"
"font: 57 13pt \"Alibaba PuHuiTi\";\n"
"\n"
"border: 0px solid;\n"
"\n"
"border-bottom: 5px solid;\n"
"\n"
"border-color: #4796f0;\n"
"\n"
"}\n"
"")
        self.tabWidget_3.setObjectName("tabWidget_3")
        self.tab_9 = QtWidgets.QWidget()
        self.tab_9.setObjectName("tab_9")
        self.tabWidget_3.addTab(self.tab_9, "")
        self.tab_10 = QtWidgets.QWidget()
        self.tab_10.setObjectName("tab_10")
        self.tabWidget_3.addTab(self.tab_10, "")
        self.tab_11 = QtWidgets.QWidget()
        self.tab_11.setObjectName("tab_11")
        self.tabWidget_3.addTab(self.tab_11, "")
        self.tab_12 = QtWidgets.QWidget()
        self.tab_12.setObjectName("tab_12")
        self.tabWidget_3.addTab(self.tab_12, "")
        self.tab_13 = QtWidgets.QWidget()
        self.tab_13.setObjectName("tab_13")
        self.tabWidget_3.addTab(self.tab_13, "")
        self.tab_14 = QtWidgets.QWidget()
        self.tab_14.setObjectName("tab_14")
        self.tabWidget_3.addTab(self.tab_14, "")
        self.tab_16 = QtWidgets.QWidget()
        self.tab_16.setObjectName("tab_16")
        self.tabWidget_3.addTab(self.tab_16, "")
        self.tableView_8 = QtWidgets.QTableView(self.tab_2)
        self.tableView_8.setGeometry(QtCore.QRect(0, 110, 661, 261))
        self.tableView_8.setStyleSheet("font: 75 9pt \"Alibaba PuHuiTi\";")
        self.tableView_8.setObjectName("tableView_8")
        self.label_18 = QtWidgets.QLabel(self.tab_2)
        self.label_18.setGeometry(QtCore.QRect(20, 110, 61, 31))
        self.label_18.setStyleSheet("color: black;\n"
"font: 57 12pt \"Alibaba PuHuiTi\";")
        self.label_18.setObjectName("label_18")
        self.pushButton_11 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_11.setGeometry(QtCore.QRect(590, 50, 71, 41))
        self.pushButton_11.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_10 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_10.setGeometry(QtCore.QRect(500, 50, 81, 41))
        self.pushButton_10.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_7 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_7.setGeometry(QtCore.QRect(200, 50, 91, 41))
        self.pushButton_7.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_8 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_8.setGeometry(QtCore.QRect(300, 50, 91, 41))
        self.pushButton_8.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_9 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_9.setGeometry(QtCore.QRect(400, 50, 91, 41))
        self.pushButton_9.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_13 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_13.setGeometry(QtCore.QRect(0, 50, 91, 41))
        self.pushButton_13.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_6 = QtWidgets.QPushButton(self.tab_2)
        self.pushButton_6.setGeometry(QtCore.QRect(100, 50, 91, 41))
        self.pushButton_6.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_6.setObjectName("pushButton_6")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.lineEdit = QtWidgets.QLineEdit(self.tab_5)
        self.lineEdit.setGeometry(QtCore.QRect(90, 10, 631, 41))
        self.lineEdit.setStyleSheet("color: white;\n"
"font: 75 12pt \"Alibaba PuHuiTi\";\n"
"background-color: rgb(38, 43, 75);")
        self.lineEdit.setObjectName("lineEdit")
        self.label_5 = QtWidgets.QLabel(self.tab_5)
        self.label_5.setGeometry(QtCore.QRect(0, 10, 91, 41))
        self.label_5.setStyleSheet("color: white;\n"
"font: 75 12pt \"Alibaba PuHuiTi\";")
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(self.tab_5)
        self.label_6.setGeometry(QtCore.QRect(0, 70, 91, 41))
        self.label_6.setStyleSheet("color: white;\n"
"font: 75 12pt \"Alibaba PuHuiTi\";")
        self.label_6.setObjectName("label_6")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.tab_5)
        self.lineEdit_2.setGeometry(QtCore.QRect(90, 70, 631, 41))
        self.lineEdit_2.setStyleSheet("color: white;\n"
"font: 75 12pt \"Alibaba PuHuiTi\";\n"
"background-color: rgb(38, 43, 75);")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_7 = QtWidgets.QLabel(self.tab_5)
        self.label_7.setGeometry(QtCore.QRect(0, 130, 71, 41))
        self.label_7.setStyleSheet("color: white;\n"
"font: 75 12pt \"Alibaba PuHuiTi\";")
        self.label_7.setObjectName("label_7")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.tab_5)
        self.lineEdit_3.setGeometry(QtCore.QRect(90, 130, 221, 41))
        self.lineEdit_3.setStyleSheet("color: white;\n"
"font: 75 12pt \"Alibaba PuHuiTi\";\n"
"background-color: rgb(38, 43, 75);")
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.pushButton_42 = QtWidgets.QPushButton(self.tab_5)
        self.pushButton_42.setGeometry(QtCore.QRect(600, 130, 121, 41))
        self.pushButton_42.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(25, 40, 50);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_42.setObjectName("pushButton_42")
        self.textBrowser_2 = QtWidgets.QTextBrowser(self.tab_5)
        self.textBrowser_2.setGeometry(QtCore.QRect(0, 180, 721, 192))
        self.textBrowser_2.setStyleSheet("font: 75 12pt \"Alibaba PuHuiTi\";")
        self.textBrowser_2.setObjectName("textBrowser_2")
        self.label_9 = QtWidgets.QLabel(self.tab_5)
        self.label_9.setGeometry(QtCore.QRect(330, 130, 81, 41))
        self.label_9.setStyleSheet("color: white;\n"
"font: 75 12pt \"Alibaba PuHuiTi\";")
        self.label_9.setObjectName("label_9")
        self.lineEdit_4 = QtWidgets.QLineEdit(self.tab_5)
        self.lineEdit_4.setGeometry(QtCore.QRect(420, 130, 161, 41))
        self.lineEdit_4.setStyleSheet("color: white;\n"
"font: 75 12pt \"Alibaba PuHuiTi\";\n"
"background-color: rgb(38, 43, 75);")
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.tabWidget.addTab(self.tab_5, "")
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 941, 521))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("res/background.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(30, 20, 151, 151))
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap("res/LOGO.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setObjectName("label_2")
        self.btn_close = QtWidgets.QPushButton(Form)
        self.btn_close.setGeometry(QtCore.QRect(860, 60, 31, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_close.sizePolicy().hasHeightForWidth())
        self.btn_close.setSizePolicy(sizePolicy)
        self.btn_close.setMinimumSize(QtCore.QSize(20, 0))
        self.btn_close.setMaximumSize(QtCore.QSize(40, 16777215))
        self.btn_close.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(25, 40, 50);\n"
"}")
        self.btn_close.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("res/close.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_close.setIcon(icon)
        self.btn_close.setObjectName("btn_close")
        self.btn_minimize = QtWidgets.QPushButton(Form)
        self.btn_minimize.setGeometry(QtCore.QRect(830, 60, 31, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn_minimize.sizePolicy().hasHeightForWidth())
        self.btn_minimize.setSizePolicy(sizePolicy)
        self.btn_minimize.setMinimumSize(QtCore.QSize(20, 0))
        self.btn_minimize.setMaximumSize(QtCore.QSize(40, 16777215))
        self.btn_minimize.setStyleSheet("QPushButton {    \n"
"    border: none;\n"
"    border-radius: 6px;\n"
"    background-color: transparent;\n"
"}\n"
"QPushButton:hover {\n"
"    background-color: rgb(52, 59, 72);\n"
"}\n"
"QPushButton:pressed {    \n"
"    background-color: rgb(25, 40, 50);\n"
"}")
        self.btn_minimize.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("res/minimize.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_minimize.setIcon(icon1)
        self.btn_minimize.setObjectName("btn_minimize")
        self.pushButton_3 = QtWidgets.QPushButton(Form)
        self.pushButton_3.setGeometry(QtCore.QRect(60, 150, 101, 41))
        self.pushButton_3.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(Form)
        self.pushButton_4.setGeometry(QtCore.QRect(60, 290, 101, 41))
        self.pushButton_4.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(Form)
        self.pushButton_5.setGeometry(QtCore.QRect(60, 220, 101, 41))
        self.pushButton_5.setStyleSheet("QPushButton {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"QPushButton:hover {\n"
"    color: black;\n"
"    border-image: url(:/button/button_selected.png);\n"
"}\n"
"QPushButton:pressed {    \n"
"    color: white;\n"
"    font: 57 12pt \"Alibaba PuHuiTi\";\n"
"    border-image: url(:/button/button_unselected.png);\n"
"}\n"
"border-image: url(:/button/button_unselected.png);")
        self.pushButton_5.setObjectName("pushButton_5")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(70, 360, 81, 31))
        self.label_3.setStyleSheet("font: 57 12pt \"Alibaba PuHuiTi\";\n"
"color: rgb(255, 255, 255);")
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Form)
        self.label_4.setGeometry(QtCore.QRect(60, 360, 101, 101))
        self.label_4.setText("")
        self.label_4.setPixmap(QtGui.QPixmap("res/square.png"))
        self.label_4.setScaledContents(True)
        self.label_4.setObjectName("label_4")
        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setGeometry(QtCore.QRect(70, 390, 81, 61))
        self.textBrowser.setStyleSheet("background-color: rgb(38, 43, 75);\n"
"color: white;\n"
"font: 57 12pt \"Alibaba PuHuiTi\";")
        self.textBrowser.setObjectName("textBrowser")
        self.label.raise_()
        self.tabWidget.raise_()
        self.label_2.raise_()
        self.btn_close.raise_()
        self.btn_minimize.raise_()
        self.pushButton_3.raise_()
        self.pushButton_4.raise_()
        self.pushButton_5.raise_()
        self.label_3.raise_()
        self.label_4.raise_()
        self.textBrowser.raise_()

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget_2.setCurrentIndex(0)
        self.tabWidget_3.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

        self.open_file_path = None
        self.open_file_name = None
        self.save_file_path = None

        # 绑定button到槽函数
        # 关闭窗口按钮
        self.btn_close.clicked.connect(self.close)
        # 最小化窗口按钮
        self.btn_minimize.clicked.connect(self.showMinimized)
        # 打开文件按钮
        self.pushButton_3.clicked.connect(self.open_file)
        # 选择查看不同编码方法的Tab
        self.tabWidget_2.currentChanged.connect(self.encodingTabChanged)
        # 选择不同功能的Tab
        # self.tabWidget.currentChanged.connect(self.examOpenFile)
        # 选择转换不同编码方法的Tab
        self.tabWidget_3.currentChanged.connect(self.decodingTabChanged)
        # 转为ASCII按钮
        self.pushButton_13.clicked.connect(self.convert2ASCII)
        # 转为UTF-8按钮
        self.pushButton_6.clicked.connect(self.convert2UTF8)
        # 转为UTF-16按钮
        self.pushButton_7.clicked.connect(self.convert2UTF16)
        # 转为GBK按钮
        self.pushButton_8.clicked.connect(self.convert2GBK)
        # 转为GB2312按钮
        self.pushButton_9.clicked.connect(self.convert2GB2312)
        # 转为Big5按钮
        self.pushButton_10.clicked.connect(self.convert2Big5)
        # 转为其它按钮
        self.pushButton_11.clicked.connect(self.convert2Else)
        # 编码开始预测按钮，绑定到多线程类上
        self.pushButton_42.clicked.connect(self.GptThread)
        # 打开帮助文档
        self.pushButton_5.clicked.connect(self.openHelpPage)
        # 打开项目仓库
        self.pushButton_4.clicked.connect(self.openGithubPage)
        # 关闭窗口按钮
        self.btn_close.clicked.connect(self.close)


    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_3), _translate("Form", "ASCII"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_4), _translate("Form", "UTF-8"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_6), _translate("Form", "UTF-16"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab), _translate("Form", "GBK"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_7), _translate("Form", "GB2312"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_8), _translate("Form", "Big5"))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_15), _translate("Form", "其它"))
        self.label_8.setText(_translate("Form", "Offset"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("Form", "编码查看"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_9), _translate("Form", "ASCII"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_10), _translate("Form", "UTF-8"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_11), _translate("Form", "UTF-16"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_12), _translate("Form", "GBK"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_13), _translate("Form", "GB2312"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_14), _translate("Form", "Big5"))
        self.tabWidget_3.setTabText(self.tabWidget_3.indexOf(self.tab_16), _translate("Form", "其它"))
        self.label_18.setText(_translate("Form", "Offset"))
        self.pushButton_11.setText(_translate("Form", "转为其它"))
        self.pushButton_10.setText(_translate("Form", "转为Big5"))
        self.pushButton_7.setText(_translate("Form", "转为UTF-16"))
        self.pushButton_8.setText(_translate("Form", "转为GBK"))
        self.pushButton_9.setText(_translate("Form", "转为GB2312"))
        self.pushButton_13.setText(_translate("Form", "转为ASCII"))
        self.pushButton_6.setText(_translate("Form", "转为UTF-8"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Form", "编码转换"))
        self.lineEdit.setText(_translate("Form", "sk-tICPHul91mqLGjpp55248e29711a4840832d494a75B1Cf19"))
        self.label_5.setText(_translate("Form", "API_KEY(*)"))
        self.label_6.setText(_translate("Form", "API_URL(*)"))
        self.lineEdit_2.setText(_translate("Form", "https://api.gpt-ai.live/v1/chat/completions"))
        self.label_7.setText(_translate("Form", "PROXY"))
        self.lineEdit_3.setText(_translate("Form", "http://127.0.0.1:7890"))
        self.pushButton_42.setText(_translate("Form", "开始/重新推测"))
        self.textBrowser_2.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Alibaba PuHuiTi\'; font-size:12pt; font-weight:72; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">暂无推测数据</p></body></html>"))
        self.label_9.setText(_translate("Form", "MODEL(*)"))
        self.lineEdit_4.setText(_translate("Form", "gpt-3.5-turbo"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("Form", "编码推测"))
        self.btn_close.setToolTip(_translate("Form", "Close"))
        self.btn_minimize.setToolTip(_translate("Form", "Minimize"))
        self.pushButton_3.setText(_translate("Form", "打开文本文件"))
        self.pushButton_4.setText(_translate("Form", "项目仓库"))
        self.pushButton_5.setText(_translate("Form", "帮助文档"))
        self.label_3.setText(_translate("Form", "当前打开："))
        self.textBrowser.setHtml(_translate("Form", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Alibaba PuHuiTi\'; font-size:12pt; font-weight:56; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:9pt;\">暂无文件</span></p></body></html>"))

    # 消息提示窗
    def showMessageBox(self,text):
        # 创建新窗口的实例
        self.form_message_box = Ui_MessageBox(text)
        # 显示新窗口
        self.form_message_box.show()

    # 查看其它编码窗
    def showDecodeChoose(self):
        # # 如果示例不存在才创建
        # if not hasattr(self, 'Ui_Decode'):
        #     # 创建新窗口的实例
        #     self.Ui_Encode = Ui_Decode(self)
        self.Ui_Decode = Ui_Decode(self)
        # 显示新窗口
        self.Ui_Decode.show()

    # 其它转换其它编码窗
    def showEncodeChoose(self):
        # # 如果示例不存在才创建
        # if not hasattr(self, 'Ui_Encode'):
        #     # 创建新窗口的实例
        #     self.Ui_Decode = Ui_Encode(self)
        self.Ui_Encode = Ui_Encode(self)
        # 显示新窗口
        self.Ui_Encode.show()

    # 已有编码转换其它编码窗
    def showConvertChoose(self):
        # # 如果示例不存在才创建
        # if not hasattr(self, 'Ui_Encode'):
        #     # 创建新窗口的实例
        #     self.Ui_Decode = Ui_Encode(self)
        self.Ui_Convert = Ui_Convert(self)
        # 显示新窗口
        self.Ui_Convert.show()

    def open_file(self):
        self.open_file_path, _ = QFileDialog.getOpenFileName(None, '打开文本文件(路径尽量不要有中文)', '', '')
        try:
            # 替换为单反斜杠
            self.open_file_path = str(self.open_file_path).replace("/", "\\").replace(":", ":")
            self.open_file_name = os.path.basename(self.open_file_path)
            # 使用 HTML 设置文本居中
            centered_text = f'<div style="text-align:center; vertical-align:middle;font-size:9pt;">{self.open_file_name}</div>'
            self.textBrowser.setHtml(centered_text)
            print("打开文件："+self.open_file_path+" 文件名："+self.open_file_name)
            # 更新编码查看窗口
            # 获取选中标签页的文本
            currentTabText = self.tabWidget_2.tabText(self.tabWidget_2.currentIndex())
            print("当前选中的encodingTab：" + currentTabText)
            # 调用 self.decode() 函数，并传入当前标签页的文本
            if self.open_file_path is not None and self.open_file_path != "":
                self.decode(str(currentTabText))
        except:
            print("取消打开文件")

    def save_file(self):
        self.save_file_path, _ = QFileDialog.getSaveFileName(None, '保存文本文件(路径尽量不要有中文)', '', '(*.txt)')
        try:
            # 替换为单反斜杠
            self.save_filepath = str(self.save_file_path).replace("/", "\\").replace(":", ":")
            print(self.save_filepath)
        except:
            print("取消保存文件")

    def decode(self,character_encoding):
        file_path = self.open_file_path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                data = file.read()
                # Suppose character_encoding is set by the user
                # character_encoding = 'utf-8'  # or any other encoding like 'utf-8', 'utf-16', 'big5', etc.
                # When setting up the model for the tableView
                hexModel = HexModel(data, character_encoding)
                self.tableView.setModel(hexModel)
                self.tableView.resizeColumnsToContents()
                self.tableView.setColumnWidth(16, 114)  # You may need to adjust this width
        else:
            print("文件不存在")

    # 检查有没有打开文本
    def examOpenFile(self):
        if self.open_file_path is not None and self.open_file_path != "":
            return True
        else:
            self.tabWidget_2.setCurrentIndex(0)
            self.tabWidget_3.setCurrentIndex(0)
            self.showMessageBox("您没有选择打开的文本")
            return False
    # 更改选中的tab时，更新表格内容
    def encodingTabChanged(self, index):
        # 获取选中标签页的文本
        currentTabText = self.tabWidget_2.tabText(index)
        print("当前选中的encodingTab："+currentTabText)
        # 调用 self.decode() 函数，并传入当前标签页的文本
        if self.examOpenFile():
            if currentTabText != "其它":
                self.decode(str(currentTabText))
            else:
                self.showDecodeChoose()

    # 测试输入的其它编码格式是否有效
    def is_valid_encoding(self,encoding_method):
        # 创建一个简单的测试字节序列
        test_bytes = b'test'
        try:
            # 尝试使用提供的编码格式进行解码
            test_bytes.decode(encoding_method)
            return True  # 未引发异常，编码格式有效
        except LookupError:
            return False

    # 转换为其它编码格式
    def convert_and_save_file(self, character_encoding, character_decoding):
        # 获取保存路径
        self.save_file()
        # 读取原始文件
        with open(self.open_file_path, 'rb') as file:
            raw_data = file.read()
        # 解码
        try:
            decoded_data = raw_data.decode(character_encoding)
        except UnicodeDecodeError:
            print("原始文件解码失败")
            self.showMessageBox(f"文本文件{self.open_file_name}以{character_encoding}解码失败")
            return
        # 重新编码
        try:
            encoded_data = decoded_data.encode(character_decoding)
        except:
            print(f"未知的编码格式: {character_decoding}")
            self.showMessageBox(f"{character_encoding}中有无法转为{character_decoding}的字符")
            return
        # 保存到新文件
        if self.save_file_path is not None and self.save_file_path != "":
            with open(self.save_file_path, 'wb') as file:
                file.write(encoded_data)
            print(f"文件已保存到 {self.save_file_path}")
            self.showMessageBox("新编码格式文件已保存")
            # 显示转换后的文件编码
            file_path = self.save_file_path
            if os.path.exists(file_path):
                with open(file_path, 'rb') as file:
                    data = file.read()
                    # Suppose character_encoding is set by the user
                    # character_encoding = 'utf-8'  # or any other encoding like 'utf-8', 'utf-16', 'big5', etc.
                    # When setting up the model for the tableView
                    hexModel = HexModel(data, character_decoding)
                    self.tableView_8.setModel(hexModel)
                    self.tableView_8.resizeColumnsToContents()
                    self.tableView_8.setColumnWidth(16, 114)  # You may need to adjust this width
            else:
                print("文件不存在")

    # 选择转换不同编码方法的Tab
    def decodingTabChanged(self, index):
        self.tableView_8.setModel(None)  # 先移除现有模型
        # 获取选中标签页的文本
        currentTabText = self.tabWidget_3.tabText(index)
        print("当前选中的decodingTab："+currentTabText)
        if currentTabText == "其它":
            if self.examOpenFile():
                self.showEncodeChoose()

    # 接下来是一堆转换按钮的实现
    def convert2ASCII(self):
        # 先检查有没有打开文本文件
        if self.examOpenFile():
            character_encoding = self.tabWidget_3.tabText(self.tabWidget_3.currentIndex())
            character_decoding = "ASCII"
            self.convert_and_save_file(character_encoding, character_decoding)

    def convert2UTF8(self):
        # 先检查有没有打开文本文件
        if self.examOpenFile():
            character_encoding = self.tabWidget_3.tabText(self.tabWidget_3.currentIndex())
            character_decoding = "UTF-8"
            self.convert_and_save_file(character_encoding, character_decoding)

    def convert2UTF16(self):
        # 先检查有没有打开文本文件
        if self.examOpenFile():
            character_encoding = self.tabWidget_3.tabText(self.tabWidget_3.currentIndex())
            character_decoding = "UTF-16"
            self.convert_and_save_file(character_encoding, character_decoding)

    def convert2GBK(self):
        # 先检查有没有打开文本文件
        if self.examOpenFile():
            character_encoding = self.tabWidget_3.tabText(self.tabWidget_3.currentIndex())
            character_decoding = "GBK"
            self.convert_and_save_file(character_encoding, character_decoding)

    def convert2GB2312(self):
        # 先检查有没有打开文本文件
        if self.examOpenFile():
            character_encoding = self.tabWidget_3.tabText(self.tabWidget_3.currentIndex())
            character_decoding = "GB2312"
            self.convert_and_save_file(character_encoding, character_decoding)

    def convert2Big5(self):
        # 先检查有没有打开文本文件
        if self.examOpenFile():
            character_encoding = self.tabWidget_3.tabText(self.tabWidget_3.currentIndex())
            character_decoding = "Big5"
            self.convert_and_save_file(character_encoding, character_decoding)

    # 打开转为其它窗口
    def convert2Else(self):
        # 先检查有没有打开文本文件
        if self.examOpenFile():
            self.showConvertChoose()

    # 打开帮助文档
    def openHelpPage(self):
         # 使用默认浏览器打开网页
        webbrowser.open("https://github.com/EricHongXDD/Universal_Encoding_Viewer/blob/main/README.md")

    # 打开仓库界面
    def openGithubPage(self):
         # 使用默认浏览器打开网页
        webbrowser.open("https://github.com/EricHongXDD/Universal_Encoding_Viewer")

    # 开始预测编码
    def GptThread(self):
        # 先检查有没有打开文本文件
        if self.examOpenFile():
            self.textBrowser_2.setText("预测中... ...请稍后... ...")
            # 实现线程类
            self.thread = GptThread(self)
            # 绑定信号量，更新预测的结果到textBrowser_2
            self.thread.string_signal.connect(self.textBrowser_2.setText)
            self.thread.finished.connect(self.thread.deleteLater)
            self.thread.start()
            # # 获取文本前64个字节用于预测
            # with open(self.open_file_path, 'rb') as file:
            #     # 读取前64个字节
            #     bytes_data = file.read(64)
            # # 将每个字节转换为16进制，并用空格隔开
            # hex_data = ' '.join(f'{byte:02x}' for byte in bytes_data)
            # # 获取参数
            # API_KEY = self.lineEdit.text()
            # API_URL = self.lineEdit_2.text()
            # PROXY = self.lineEdit_3.text()
            # # 开始预测
            # analyze_result = analyze_gpt(API_KEY, API_URL, PROXY, hex_data)
