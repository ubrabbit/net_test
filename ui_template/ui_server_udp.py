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
import ui_template.ui_server_tcp

import func_server


def init_template(parent):
        obj_ui = CInterfaceUnit(parent)
        obj_ui.init_interface()
        return obj_ui.get_mainWidget()


class CInterfaceUnit(ui_template.ui_server_tcp.CInterfaceUnit):


    def init_interface(self):
        self.main_Layout=QtGui.QVBoxLayout(self.get_mainWidget())

        layout_Horizon_2 = QtGui.QHBoxLayout( )
        layout_Horizon_3 = QtGui.QHBoxLayout( )

        self.main_Layout.addLayout( layout_Horizon_2 )
        self.main_Layout.addLayout( layout_Horizon_3 )
        self.main_Layout.setStretchFactor( layout_Horizon_2,3 )
        self.main_Layout.setStretchFactor( layout_Horizon_3,7 )

        label_udp = self.new_label("UDP服务器")
        label_udp_port = self.new_label("UDP端口")
        label_udp_output = self.new_label("UDP服务器输出")

        self.lineEdit_udp_server = QtGui.QLineEdit()
        self.lineEdit_udp_port = QtGui.QLineEdit()

        self.fileEdit_udp = QtGui.QTextEdit()

        self.button_udp_server = QtGui.QPushButton(self.tr("开启"))

        layout_Vector_2_0 = QtGui.QVBoxLayout()

        layout_Horizon_2_0 = QtGui.QHBoxLayout( )
        layout_Horizon_2_1 = QtGui.QHBoxLayout( )

        layout_Horizon_2.addWidget( label_udp )
        layout_Horizon_2.addWidget( self.lineEdit_udp_server )
        layout_Horizon_2.addWidget( label_udp_port )
        layout_Horizon_2.addWidget( self.lineEdit_udp_port )
        layout_Horizon_2.addWidget( self.button_udp_server )
        layout_Horizon_2.addStretch(1)

        layout_Horizon_3.addLayout( layout_Vector_2_0 )

        label_udp_client = self.new_label("设置UDP返回包")

        self.fileEdit_udp_client = QtGui.QTextEdit()

        layout_Horizon_2_0.addWidget( label_udp_client )
        layout_Horizon_2_0.addStretch(2)
        layout_Horizon_2_1.addWidget( self.fileEdit_udp_client )

        layout_Vector_2_0.addLayout( layout_Horizon_2_0 )
        layout_Vector_2_0.addLayout( layout_Horizon_2_1 )
        layout_Vector_2_0.addWidget( label_udp_output )
        layout_Vector_2_0.addWidget( self.fileEdit_udp )
        layout_Vector_2_0.setStretchFactor( layout_Horizon_2_0,1 )
        layout_Vector_2_0.setStretchFactor( layout_Horizon_2_1,2 )
        layout_Vector_2_0.setStretchFactor( label_udp_output,1 )
        layout_Vector_2_0.setStretchFactor(  self.fileEdit_udp,6 )
        layout_Vector_2_0.addStretch(2)

        self.lineEdit_udp_server.setText("127.0.0.1")
        self.lineEdit_udp_port.setText("10002")

        funcobj = partial_functor( self.on_udp_packet_handler )
        func_server.regist_event( "udp", "packet", "exec_packet", funcobj )

        #---------------------------- signal -----------------------------------------
        self.button_udp_server.clicked.connect( partial(self.on_button_clicked,"udp_server") )


    def on_button_clicked(self, flag_name):
        flag_name = str(flag_name)
        print "on_button_clicked"

        if flag_name=="udp_server":
            server_ip = self.get_string(self.lineEdit_udp_server.text())
            server_port = self.get_string(self.lineEdit_udp_port.text())

            func_server.reset_buffer( self.fileEdit_udp )
            func_server.start_udp_server( server_ip, server_port )


    def on_udp_packet_handler(self, obj_conn, message):
        print "on_udp_packet_handler  ",obj_conn, message

        respond_packet = self.get_string( self.fileEdit_udp_client.toPlainText() )
        obj_conn.send_packet( respond_packet )
