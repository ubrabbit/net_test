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

        label_tcp = self.new_label("TCP服务器")
        label_udp = self.new_label("UDP服务器")
        label_tcp_output = self.new_label("TCP服务器输出")
        label_udp_output = self.new_label("UDP服务器输出")

        self.lineEdit_tcp_server = QtGui.QLineEdit()
        self.lineEdit_tcp_port = QtGui.QLineEdit()
        self.lineEdit_udp_server = QtGui.QLineEdit()
        self.lineEdit_udp_port = QtGui.QLineEdit()

        self.fileEdit_tcp = QtGui.QTextEdit()
        self.fileEdit_udp = QtGui.QTextEdit()

        self.button_tcp = QtGui.QPushButton(self.tr("开启"))
        self.button_udp = QtGui.QPushButton(self.tr("开启"))
    