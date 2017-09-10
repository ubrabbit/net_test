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


def init_template(parent):
        obj_ui = CInterfaceUnit(parent)
        obj_ui.init_interface()
        return obj_ui.get_mainWidget()


class CConnClient( CNotifyObject ):

    def __init__(self, parent, protocol):
        super( CConnClient, self ).__init__()
        self.parent = parent
        self.protocol = protocol
        self.tcp_client_list = {}


    def __del__(self):
        for client_key in self.get_alive_tcp_client_list():
            client_obj = self.tcp_client_list[ client_key ]
            safe_call( client_obj.do_disconnect )


    def get_tcp_client(self, client_key):
        if not client_key in self.tcp_client_list:
            return None
        return self.tcp_client_list[ client_key ]


    def get_alive_tcp_client_list(self):
        key_list = self.tcp_client_list.keys()
        for client_key in key_list:
            client_obj = self.tcp_client_list[ client_key ]
            if not client_obj.is_active():
                del self.tcp_client_list[ client_key ]
        return self.tcp_client_list.keys()


    def connect_tcp_server(self, server_ip, server_port):
        client_obj = func_client_tcp.tcp_new_connect( server_ip, server_port )

        funcobj = partial_functor( self.on_client_conn_handler, "client_conn" )
        client_obj.regist_event("tcp","client_conn","exec_conn",funcobj)

        funcobj = partial_functor( self.on_client_conn_handler, "client_disconn" )
        client_obj.regist_event("tcp","client_disconn","exec_disconn",funcobj)

        return client_obj


    def on_client_conn_handler(self, event_key, ip, port, client_obj):
        client_key = "%s:%s  -->  %s:%s"%(ip,port,client_obj.ip,client_obj.port)

        print "on_client_conn_handler ",client_key, event_key
        if event_key == "client_conn":
            self.tcp_client_list[ client_key ] = client_obj
        elif event_key == "client_disconn":
            if client_key in self.tcp_client_list:
                del self.tcp_client_list[ client_key ]

        self.parent.on_client_conn_handler( event_key, client_key, client_obj )


    def send_packet(self, client_key, server_ip, server_port, packet_input):
        if self.protocol == "tcp":
            client_obj = self.tcp_client_list.get(client_key, None)
            if not client_obj or not client_obj.is_active():
                client_obj = self.connect_tcp_server( server_ip, server_port )
            idx = 0
            idx = client_obj.get_idx()
            func_client_tcp.tcp_send_packet( server_ip, server_port, packet_input, idx )

        elif self.protocol == "udp":
            func_client_udp.udp_send_packet( server_ip, server_port, packet_input )


class CInterfaceUnit(ui_template.CTemplateBase):


    def __init__(self, parent):
        super( CInterfaceUnit, self).__init__( parent )
        self.conn_obj_tcp = None
        self.conn_obj_udp = None


    def init_interface(self):
        self.main_Layout = QtGui.QVBoxLayout(self.get_mainWidget())

        layout_Horizon_0 = QtGui.QHBoxLayout( )
        layout_Horizon_1 = QtGui.QHBoxLayout( )
        layout_Horizon_2 = QtGui.QHBoxLayout( )
        layout_Horizon_3 = QtGui.QHBoxLayout( )

        layout_Vector_2_0 = QtGui.QVBoxLayout()
        layout_Vector_2_1 = QtGui.QVBoxLayout()

        layout_Horizon_2_0_0 = QtGui.QHBoxLayout( )
        layout_Horizon_2_0_1 = QtGui.QHBoxLayout( )
        layout_Horizon_2_0_2 = QtGui.QHBoxLayout( )
        layout_Horizon_2_0_3 = QtGui.QHBoxLayout( )

        self.main_Layout.addLayout( layout_Horizon_0 )
        self.main_Layout.addLayout( layout_Horizon_1 )
        self.main_Layout.addLayout( layout_Horizon_3 )
        self.main_Layout.addLayout( layout_Horizon_2 )

        layout_Horizon_2.addLayout( layout_Vector_2_0 )
        layout_Horizon_2.addLayout( layout_Vector_2_1 )

        label_proto = self.new_label("选择协议：")
        label_server = self.new_label("服务器地址：")
        label_port = self.new_label("服务器端口：")
        label_input = self.new_label("输入：")
        label_output = self.new_label("输出：")

        self.button_conn = QtGui.QPushButton(self.tr("新建连接"))
        self.button_disconn = QtGui.QPushButton(self.tr("断开连接"))
        self.button_send = QtGui.QPushButton(self.tr("发送"))

        self.combo_protocol = self.new_combo()

        self.lineEdit_server = QtGui.QLineEdit()
        self.lineEdit_port = QtGui.QLineEdit()

        self.fileEdit_input = QtGui.QTextEdit()
        self.fileEdit_output = QtGui.QTextEdit()

        self.listWidget_client_list = QtGui.QListWidget()

        layout_Horizon_0.addWidget( label_proto )
        layout_Horizon_0.addWidget( self.combo_protocol.get_mainWidget() )
        layout_Horizon_0.addStretch(2)

        layout_Horizon_1.addWidget( label_server )
        layout_Horizon_1.addWidget( self.lineEdit_server )
        layout_Horizon_1.addWidget( label_port )
        layout_Horizon_1.addWidget( self.lineEdit_port )
        layout_Horizon_1.addWidget( self.button_conn )

        layout_Horizon_2_0_0.addWidget( label_input )
        layout_Horizon_2_0_0.addWidget( self.button_send )
        layout_Horizon_2_0_0.addStretch(2)

        layout_Horizon_2_0_1.addWidget( self.fileEdit_input )

        layout_Horizon_2_0_2.addWidget( label_output )
        layout_Horizon_2_0_3.addWidget( self.fileEdit_output )

        layout_Vector_2_0.addLayout( layout_Horizon_2_0_0 )
        layout_Vector_2_0.addLayout( layout_Horizon_2_0_1 )
        layout_Vector_2_0.addLayout( layout_Horizon_2_0_2 )
        layout_Vector_2_0.addLayout( layout_Horizon_2_0_3 )

        layout_Vector_2_0.setStretchFactor( layout_Horizon_2_0_0,1 )
        layout_Vector_2_0.setStretchFactor( layout_Horizon_2_0_1,2 )
        layout_Vector_2_0.setStretchFactor( layout_Horizon_2_0_2,1 )
        layout_Vector_2_0.setStretchFactor( layout_Horizon_2_0_3,6 )

        #layout_Vector_2_1.addWidget( self.button_send )
        #layout_Vector_2_1.addStretch(2)

        layout_Vector_3_0 = QtGui.QVBoxLayout( )
        layout_Vector_3_1 = QtGui.QVBoxLayout( )
        layout_Horizon_3.addLayout( layout_Vector_3_0 )
        layout_Horizon_3.addLayout( layout_Vector_3_1 )

        layout_Vector_3_0.addWidget( self.listWidget_client_list )
        layout_Vector_3_1.addWidget( self.button_disconn )
        layout_Vector_3_1.addStretch( 1 )

        self.combo_protocol.init_select( ["tcp","udp"] )
        self.combo_protocol.active_event( partial(self.on_combo_actived,"protocol") )
        self.combo_protocol.set_select_by_name( "tcp" )
        self.conn_obj_tcp = CConnClient(self, "tcp")
        self.conn_obj_udp = CConnClient(self, "udp")

        self.lineEdit_server.setText("127.0.0.1")
        self.lineEdit_port.setText("10001")

        func_client_tcp.reset_buffer( self.fileEdit_output )
        func_client_udp.reset_buffer( self.fileEdit_output )

        #---------------------------- signal -----------------------------------------
        self.button_conn.clicked.connect( partial(self.on_button_clicked,"connect") )
        self.button_disconn.clicked.connect( partial(self.on_button_clicked,"disconnect") )
        self.button_send.clicked.connect( partial(self.on_button_clicked,"send") )

        self.listWidget_client_list.itemClicked.connect( partial(self.select_clientobj) )


    def select_clientobj(self):
        print "select_clientobj "


    def get_select_client_key(self):
        current_row = self.listWidget_client_list.currentRow()
        obj_item = self.listWidget_client_list.currentItem()
        if not obj_item:
                return ""
        client_key = self.get_string(obj_item.text())
        return client_key


    def on_button_clicked(self, flag_name):
        flag_name = str(flag_name)
        obj_cfg = get_config_obj()
        if flag_name=="connect":
            self.connect_tcp_server()

        elif flag_name=="send":
            self.send_packet()

        elif flag_name=="disconnect":
            client_key = self.get_select_client_key()
            if not client_key:
                return None
            client_obj = self.conn_obj_tcp.get_tcp_client( client_key )
            if not client_obj:
                return None
            safe_call( client_obj.do_disconnect )


    def on_combo_actived(self,flag_name,value):
        flag_name = str(flag_name)
        value=str(value)
        print "on_combo_actived ",flag_name,value
        if flag_name=="protocol":
            protocol = self.get_string( self.combo_protocol.get_select_text() )

            if protocol == "udp":
                self.button_conn.setEnabled(False)
                self.lineEdit_server.setText("127.0.0.1")
                self.lineEdit_port.setText("10002")
            elif protocol == "tcp":
                self.button_conn.setEnabled(True)
                self.lineEdit_server.setText("127.0.0.1")
                self.lineEdit_port.setText("10001")

    def connect_tcp_server(self):
        server_ip = self.get_string(self.lineEdit_server.text())
        server_port = self.get_string(self.lineEdit_port.text())

        print "connect_tcp_server ",server_ip,server_port
        self.conn_obj_tcp.connect_tcp_server( server_ip, server_port )


    def send_packet(self):
        protocol = self.get_string( self.combo_protocol.get_select_text() )
        server_ip = self.get_string( self.lineEdit_server.text() )
        server_port = self.get_string( self.lineEdit_port.text() )
        packet_input = self.get_string( self.fileEdit_input.toPlainText() )

        if protocol == "tcp":
            client_key = self.get_select_client_key()
            self.conn_obj_tcp.send_packet( client_key, server_ip,server_port,packet_input )
        else:
            self.conn_obj_udp.send_packet( "", server_ip,server_port,packet_input )


    def on_client_conn_handler(self, event_key, client_key, client_obj):
        print "parent on_client_conn_handler ",client_key, event_key
        if event_key == "client_conn":
            self.listWidget_client_list.addItem(QtGui.QListWidgetItem(self.tr(client_key)))

        elif event_key == "client_disconn":
            while self.listWidget_client_list.count() > 0:
                self.listWidget_client_list.takeItem( 0 )

            new_key_list = self.conn_obj_tcp.get_alive_tcp_client_list()
            for client_key in new_key_list:
                self.listWidget_client_list.addItem(QtGui.QListWidgetItem(self.tr(client_key)))
