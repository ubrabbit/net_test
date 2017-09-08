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

            self.conn_pool = {}


    def init_interface(self):
        self.main_Layout=QtGui.QVBoxLayout(self.get_mainWidget())

        layout_Horizon_0 = QtGui.QHBoxLayout( )
        layout_Horizon_1 = QtGui.QHBoxLayout( )
        layout_Horizon_2 = QtGui.QHBoxLayout( )
        layout_Horizon_3 = QtGui.QHBoxLayout( )
        
        layout_Vector_4 = QtGui.QVBoxLayout()

        self.main_Layout.addLayout( layout_Horizon_0 )
        self.main_Layout.addLayout( layout_Vector_4 )
        self.main_Layout.addLayout( layout_Horizon_1 )
        self.main_Layout.addLayout( layout_Horizon_2 )
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
        layout_Vector_2_2 = QtGui.QVBoxLayout()

        layout_Horizon_2_0 = QtGui.QHBoxLayout( )
        layout_Horizon_2_1 = QtGui.QHBoxLayout( )

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
        label_tcp_input = self.new_label("设置TCP包：")
        label_udp_client = self.new_label("设置UDP返回包")
        self.combo_tcp_client = self.new_combo()

        self.fileEdit_tcp_client = QtGui.QTextEdit()
        self.fileEdit_udp_client = QtGui.QTextEdit()

        self.button_tcp_client = QtGui.QPushButton(self.tr("发送数据"))

        layout_Horizon_4_0 = QtGui.QHBoxLayout( )
        layout_Horizon_4_1 = QtGui.QHBoxLayout( )
        layout_Horizon_4_2 = QtGui.QHBoxLayout( )

        layout_Horizon_4_0.addWidget( label_tcp_client )
        layout_Horizon_4_0.addWidget( self.combo_tcp_client.get_mainWidget() )
        layout_Horizon_4_0.addStretch(1)

        layout_Horizon_4_1.addWidget( label_tcp_input )
        layout_Horizon_4_1.addWidget( self.button_tcp_client )
        layout_Horizon_4_1.addStretch(1)

        layout_Horizon_4_2.addWidget( self.fileEdit_tcp_client )

        layout_Vector_4.addLayout( layout_Horizon_4_0 )
        layout_Vector_4.addLayout( layout_Horizon_4_1 )
        layout_Vector_4.addLayout( layout_Horizon_4_2 )
        layout_Vector_4.setStretchFactor( layout_Horizon_4_0,1 )
        layout_Vector_4.setStretchFactor( layout_Horizon_4_1,2 )
        layout_Vector_4.setStretchFactor( layout_Horizon_4_2,7 )

        layout_Horizon_2_0.addWidget( label_udp_client )
        layout_Horizon_2_0.addStretch(2)
        layout_Horizon_2_1.addWidget( self.fileEdit_udp_client )

        layout_Vector_1_0.addWidget( label_tcp_output )
        layout_Vector_1_0.addWidget( self.fileEdit_tcp )
        layout_Vector_1_1.addStretch(2)

        layout_Vector_2_0.addLayout( layout_Horizon_2_0 )
        layout_Vector_2_0.addLayout( layout_Horizon_2_1 )
        layout_Vector_2_0.addWidget( label_udp_output )
        layout_Vector_2_0.addWidget( self.fileEdit_udp )
        layout_Vector_2_0.setStretchFactor( layout_Horizon_2_0,1 )
        layout_Vector_2_0.setStretchFactor( layout_Horizon_2_1,2 )
        layout_Vector_2_0.setStretchFactor( label_udp_output,1 )
        layout_Vector_2_0.setStretchFactor(  self.fileEdit_udp,6 )
        layout_Vector_2_1.addStretch(2)

        self.lineEdit_tcp_server.setText("127.0.0.1")
        self.lineEdit_tcp_port.setText("10001")

        self.lineEdit_udp_server.setText("127.0.0.1")
        self.lineEdit_udp_port.setText("10002")

        funcobj = partial_functor( self.on_tcp_connect_handler, "connect" )
        func_server.regist_event( "tcp", "connect", "exec_conn", funcobj )

        funcobj = partial_functor( self.on_tcp_connect_handler, "disconnect" )
        func_server.regist_event( "tcp", "disconnect", "exec_disconn", funcobj )

        funcobj = partial_functor( self.on_tcp_packet_handler )
        func_server.regist_event( "tcp", "packet", "exec_packet", funcobj )

        funcobj = partial_functor( self.on_udp_packet_handler )
        func_server.regist_event( "udp", "packet", "exec_packet", funcobj )

        #---------------------------- signal -----------------------------------------
        self.button_tcp_server.clicked.connect( partial(self.on_button_clicked,"tcp_server") )
        self.button_udp_server.clicked.connect( partial(self.on_button_clicked,"udp_server") )
        self.button_tcp_client.clicked.connect( partial(self.on_button_clicked,"tcp_client") )


    def on_button_clicked(self, flag_name):
        flag_name = str(flag_name)
        print "on_button_clicked"
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
            client_key = self.get_string( self.combo_tcp_client.get_select_text() )
            if not client_key:
                self.error("","未选择客户端")
                return
            if not client_key in self.conn_pool:
                self.error("","连接已失效")
                return
            obj_conn = self.conn_pool[client_key]
            if not obj_conn.is_active():
                self.error("","连接已失效")
                return
            message = self.get_string( self.fileEdit_tcp_client.toPlainText() )
            obj_conn.send_packet( message )
            self.info("","发送成功")


    def on_tcp_connect_handler(self, event_key, obj_conn):
        print "on_tcp_connect_handler  ",event_key, obj_conn
        ip, port = obj_conn.ip,int(obj_conn.port)
        key = "%s:%s"%(ip,port)
        if event_key == "connect":
            self.conn_pool[ key ] = obj_conn
        elif event_key == "disconnect" and key in self.conn_pool:
            del self.conn_pool[ key ]

        client_list = self.conn_pool.keys()
        self.combo_tcp_client.init_select( client_list )


    def on_tcp_packet_handler(self, obj_conn, message):
        print "on_tcp_packet_handler  ",obj_conn, message
        #obj_conn.send_packet( "BBCC" )


    def on_udp_packet_handler(self, obj_conn, message):
        print "on_udp_packet_handler  ",obj_conn, message

        respond_packet = self.get_string( self.fileEdit_udp_client.toPlainText() )
        obj_conn.send_packet( respond_packet )
