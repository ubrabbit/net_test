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

        self.checkBox_hex = QtGui.QCheckBox('使用16进制压解包', self.get_mainWidget())
        layout_Horizon_0.addWidget( self.checkBox_hex )
        layout_Horizon_0.addStretch(2)

        self.main_Layout.addLayout( layout_Horizon_0 )
        self.main_Layout.addLayout( layout_Horizon_1 )
        self.main_Layout.addStretch(2)

        obj_config = get_config_obj()
        obj_config.set_packet_mode("hex")

        # 将用户定义的changeTitle()函数与单选框的stateChanged()信号连接起来。
        self.checkBox_hex.toggle()  #初始是设置了的
        self.m_Parent.connect(self.checkBox_hex, QtCore.SIGNAL('stateChanged(int)'), partial(self.select_packet_mode) )


    def select_packet_mode(self):
        obj_config = get_config_obj()
        if self.checkBox_hex.isChecked():
            print "set hex mode"
            obj_config.set_packet_mode("hex")
        else:
            print "set ascii mode"
            obj_config.set_packet_mode("ascii")
