#coding: utf-8

"""
"""

import sys
import copy
import math
import re

import traceback
from functools import partial

from PyQt4 import QtCore, QtGui

from common import *

import ui_template

import func_server


def init_template(parent):
        obj_ui = CInterfaceUnit(parent)
        obj_ui.init_interface()
        return obj_ui.get_mainWidget()


class CInterfaceUnit(ui_template.CTemplateBase):


    def __init__(self, parent):
            super( CInterfaceUnit, self).__init__( parent )


    def init_interface(self):
        self.main_Layout=QtGui.QVBoxLayout(self.get_mainWidget())

        layout_Horizon_0 = QtGui.QHBoxLayout( )
        layout_Horizon_1 = QtGui.QHBoxLayout( )
        layout_Horizon_2 = QtGui.QHBoxLayout( )
        layout_Horizon_3 = QtGui.QHBoxLayout( )
        layout_Horizon_4 = QtGui.QHBoxLayout( )
        layout_Horizon_5 = QtGui.QHBoxLayout( )

        self.main_Layout.addLayout( layout_Horizon_0 )
        self.main_Layout.addLayout( layout_Horizon_4 )
        self.main_Layout.addLayout( layout_Horizon_1 )
        self.main_Layout.addLayout( layout_Horizon_2 )
        self.main_Layout.addLayout( layout_Horizon_5 )
        self.main_Layout.addLayout( layout_Horizon_3 )

        label_tcp = self.new_label("TCP服务器")
        label_tcp_port = self.new_label("TCP端口")
        label_udp = self.new_label("UDP服务器")
        label_udp_port = self.new_label("UDP端口")
        label_tcp_output = self.new_label("TCP服务器输出")
        label_udp_output = self.new_label("UDP服务器输出")

        self.lineEdit_tcp_server = QtGui.QLineEdit()
        self.lineEdit_tcp_port = QtGui.QLineEdit()
        self.lineEdit_udp_server = QtGui.QLineEdit()
        self.lineEdit_udp_port = QtGui.QLineEdit()

        self.fileEdit_tcp = QtGui.QTextEdit()
        self.fileEdit_udp = QtGui.QTextEdit()

        self.button_tcp_server = QtGui.QPushButton(self.tr("开启"))
        self.button_udp_server = QtGui.QPushButton(self.tr("开启"))

        layout_Vector_1_0 = QtGui.QVBoxLayout()
        layout_Vector_1_1 = QtGui.QVBoxLayout()
        layout_Vector_2_0 = QtGui.QVBoxLayout()
        layout_Vector_2_1 = QtGui.QVBoxLayout()

        layout_Vector_1_0.addWidget( self.fileEdit_tcp )
        layout_Vector_1_1.addWidget( self.button_tcp_server )
        layout_Vector_1_1.addStretch(2)

        layout_Vector_2_0.addWidget( self.fileEdit_udp )
        layout_Vector_2_1.addWidget( self.button_udp_server )
        layout_Vector_2_1.addStretch(2)

        layout_Horizon_0.addWidget( label_tcp )
        layout_Horizon_0.addWidget( self.lineEdit_tcp_server )
        layout_Horizon_0.addWidget( label_tcp_port )
        layout_Horizon_0.addWidget( self.lineEdit_tcp_port )
        layout_Horizon_0.addWidget( self.button_tcp_server )
        layout_Horizon_0.addStretch(1)

        layout_Horizon_1.addLayout( layout_Vector_1_0 )
        layout_Horizon_1.addLayout( layout_Vector_1_1 )

        layout_Horizon_2.addWidget( label_udp )
        layout_Horizon_2.addWidget( self.lineEdit_udp_server )
        layout_Horizon_2.addWidget( label_udp_port )
        layout_Horizon_2.addWidget( self.lineEdit_udp_port )
        layout_Horizon_2.addWidget( self.button_udp_server )
        layout_Horizon_2.addStretch(1)

        layout_Horizon_3.addLayout( layout_Vector_2_0 )
        layout_Horizon_3.addLayout( layout_Vector_2_1 )

        label_tcp_client = self.new_label("选择TCP客户端连接：")
        self.combo_tcp_client = self.new_combo()

        self.lineEdit_tcp_client = QtGui.QLineEdit()
        self.lineEdit_udp_client = QtGui.QLineEdit()

        self.button_tcp_client = QtGui.QPushButton(self.tr("发送数据"))
        self.button_udp_client = QtGui.QPushButton(self.tr("设置UDP返回包"))

        layout_Horizon_4.addWidget( label_tcp_client )
        layout_Horizon_4.addWidget( self.combo_tcp_client.get_mainWidget() )
        layout_Horizon_4.addWidget( self.lineEdit_tcp_client )
        layout_Horizon_4.addWidget( self.button_tcp_client )

        layout_Horizon_5.addWidget( self.button_udp_client )
        layout_Horizon_5.addWidget( self.lineEdit_udp_client )

        self.lineEdit_tcp_server.setText("127.0.0.1")
        self.lineEdit_tcp_port.setText("10001")

        self.lineEdit_udp_server.setText("127.0.0.1")
        self.lineEdit_udp_port.setText("10002")

        #---------------------------- signal -----------------------------------------
        self.button_tcp_server.clicked.connect( partial(self.on_button_clicked,"tcp_server") )
        self.button_udp_server.clicked.connect( partial(self.on_button_clicked,"udp_server") )
        self.button_tcp_client.clicked.connect( partial(self.on_button_clicked,"tcp_client") )
        self.button_udp_client.clicked.connect( partial(self.on_button_clicked,"udp_client") )


    def on_button_clicked(self, flag_name):
        flag_name = str(flag_name)

        if flag_name=="tcp_server":
            server_ip = self.get_string(self.lineEdit_tcp_server.text())
            server_port = self.get_string(self.lineEdit_tcp_port.text())

            func_server.reset_buffer( self.fileEdit_tcp )
            func_server.start_tcp_server( server_ip, server_port )

        elif flag_name=="udp_server":
            server_ip = self.get_string(self.lineEdit_udp_server.text())
            server_port = self.get_string(self.lineEdit_udp_port.text())

            func_server.reset_buffer( self.fileEdit_udp )
            func_server.start_udp_server( server_ip, server_port )

        elif flag_name=="tcp_client":
            pass

        elif flag_name=="udp_client":
            pass
