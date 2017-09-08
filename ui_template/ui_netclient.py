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


import func_client_tcp
import func_client_udp
import func_server


def init_template(parent):
        obj_ui = CInterfaceUnit(parent)
        obj_ui.init_interface()
        return obj_ui.get_mainWidget()


class CConnClient(object):

    def __init__(self, protocol):
        self.protocol = protocol
        self.client_obj = None


    def connect_tcp_server(self, server_ip, server_port):
        self.client_obj = func_client_tcp.tcp_new_connect( server_ip, server_port )


    def send_packet(self, server_ip, server_port, packet_input):
        if self.protocol == "tcp":
            idx = 0
            if self.client_obj and self.client_obj.is_active():
                idx = self.client_obj.get_idx()
            self.client_obj = func_client_tcp.tcp_send_packet( server_ip, server_port, packet_input, idx )
        elif self.protocol == "udp":
            func_client_udp.udp_send_packet( server_ip, server_port, packet_input )


class CInterfaceUnit(ui_template.CTemplateBase):


    def __init__(self, parent):
        super( CInterfaceUnit, self).__init__( parent )
        self.conn_obj = None


    def init_interface(self):
        self.main_Layout = QtGui.QVBoxLayout(self.get_mainWidget())

        layout_Horizon_0 = QtGui.QHBoxLayout( )
        layout_Horizon_1 = QtGui.QHBoxLayout( )
        layout_Horizon_2 = QtGui.QHBoxLayout( )

        layout_Vector_2_0 = QtGui.QVBoxLayout()
        layout_Vector_2_1 = QtGui.QVBoxLayout()

        layout_Horizon_2_0_0 = QtGui.QHBoxLayout( )
        layout_Horizon_2_0_1 = QtGui.QHBoxLayout( )
        layout_Horizon_2_0_2 = QtGui.QHBoxLayout( )
        layout_Horizon_2_0_3 = QtGui.QHBoxLayout( )

        self.main_Layout.addLayout( layout_Horizon_0 )
        self.main_Layout.addLayout( layout_Horizon_1 )
        self.main_Layout.addLayout( layout_Horizon_2 )

        layout_Horizon_2.addLayout( layout_Vector_2_0 )
        layout_Horizon_2.addLayout( layout_Vector_2_1 )

        label_proto = self.new_label("选择协议：")
        label_server = self.new_label("服务器地址：")
        label_port = self.new_label("服务器端口：")
        label_input = self.new_label("输入(忽略所有空格及换行符)：")
        label_output = self.new_label("输出：")

        self.button_conn = QtGui.QPushButton(self.tr("连接"))
        self.button_send = QtGui.QPushButton(self.tr("发送"))

        self.combo_protocol = self.new_combo()

        self.lineEdit_server = QtGui.QLineEdit()
        self.lineEdit_port = QtGui.QLineEdit()

        self.fileEdit_input = QtGui.QTextEdit()
        self.fileEdit_output = QtGui.QTextEdit()

        layout_Horizon_0.addWidget( label_proto )
        layout_Horizon_0.addWidget( self.combo_protocol.get_mainWidget() )
        layout_Horizon_0.addStretch(2)

        layout_Horizon_1.addWidget( label_server )
        layout_Horizon_1.addWidget( self.lineEdit_server )
        layout_Horizon_1.addWidget( label_port )
        layout_Horizon_1.addWidget( self.lineEdit_port )
        layout_Horizon_1.addWidget( self.button_conn )

        layout_Horizon_2_0_0.addWidget( label_input )
        layout_Horizon_2_0_1.addWidget( self.fileEdit_input )

        layout_Horizon_2_0_2.addWidget( label_output )
        layout_Horizon_2_0_3.addWidget( self.fileEdit_output )

        layout_Vector_2_0.addLayout( layout_Horizon_2_0_0 )
        layout_Vector_2_0.addLayout( layout_Horizon_2_0_1 )
        layout_Vector_2_0.addLayout( layout_Horizon_2_0_2 )
        layout_Vector_2_0.addLayout( layout_Horizon_2_0_3 )

        layout_Vector_2_1.addWidget( self.button_send )
        layout_Vector_2_1.addStretch(2)

        self.combo_protocol.init_select( ["tcp","udp"] )
        self.combo_protocol.active_event( partial(self.on_combo_actived,"protocol") )
        self.combo_protocol.set_select_by_name( "tcp" )
        self.conn_obj = CConnClient("tcp")

        #---------------------------- signal -----------------------------------------
        self.button_conn.clicked.connect( partial(self.on_button_clicked,"connect") )
        self.button_send.clicked.connect( partial(self.on_button_clicked,"send") )


    def on_button_clicked(self, flag_name):
        flag_name = str(flag_name)
        obj_cfg = get_config_obj()
        if flag_name=="connect":
            self.connect_tcp_server()
        elif flag_name=="send":
            self.send_packet()


    def on_combo_actived(self,flag_name,value):
        flag_name = str(flag_name)
        value=str(value)
        print "on_combo_actived ",flag_name,value
        if flag_name=="protocol":
            protocol = self.get_string( self.combo_protocol.get_select_text() )
            self.conn_obj = CConnClient(protocol)

            if protocol == "udp":
                self.button_conn.setEnabled(False)
            elif protocol == "tcp":
                self.button_conn.setEnabled(True)


    def connect_tcp_server(self):
        server_ip = self.get_string(self.lineEdit_server.text())
        server_port = self.get_string(self.lineEdit_port.text())
        print "connect_tcp_server ",server_ip,server_port

        self.conn_obj.connect_tcp_server( server_ip, server_port )


    def send_packet(self):
        protocol = self.get_string( self.combo_protocol.get_select_text() )
        server_ip = self.get_string( self.lineEdit_server.text() )
        server_port = self.get_string( self.lineEdit_port.text() )
        packet_input = self.get_string( self.fileEdit_input.toPlainText() )

        print "send_packet ",server_ip,server_port,packet_input
        self.conn_obj.send_packet( server_ip,server_port,packet_input )
