#coding: utf-8

"""
"""

import sys
import os
import copy
import math
import re

import traceback
from functools import partial

from PyQt4 import QtCore, QtGui

from common import *


class CObjectBase(object):

        def __init__(self, parent):
                super(CObjectBase, self).__init__()
                self.m_Parent = parent


        def tr(self,msg):
                return self.m_Parent.tr(msg)


        def info(self, title, msg):
                self.m_Parent.info(title,msg)


        def critical(self, title, msg):
                self.m_Parent.critical(title,msg)


        def error(self, title, msg):
                self.m_Parent.critical(title,msg)


        def warning(self, title, msg):
                self.m_Parent.warning(title,msg)


        def get_string(self, code):
                if isinstance(code, QtCore.QString):
                        return unicode(code, 'utf-8', 'ignore').encode("utf-8")
                return get_string( code )


        def get_other_save_file(self,base_name=True):
                #参数里有三个QStrng类型的参数，第一个代表弹出对话框的标题；第二是默认的路径，
                #如果空，则默认为当前路径；第三个是代表了过滤器，如果要有多个过滤器的话，
                #可以用”::”分割，如："Images (*.png *.xpm *.jpg);;Text files (*.txt);;XML files (*.xml)"
                #得到的fileName就是我们选择的文件和它的路径，类型为QString

                sFilter="All Files(*);;Header Files(*.header *.body *.attach *.eml *.txt);;Py Files(*.py *.txt);;Image Files(*.png *.jpg *.bmp);; C++ Files(*.txt *.cpp *.c *.h)"
                #fileName=QtGui.QFileDialog.getOpenFileName(self,self.tr("打开文件"),QtCore.QString(),self.tr(sFilter))
                default_path = "%s/unname"%(get_templatepath())
                file_name=QtGui.QFileDialog.getSaveFileName(self.m_Parent,self.tr("保存文件"),QtCore.QString(default_path),self.tr(sFilter))
                file_name=unicode(file_name, 'utf8', 'ignore').encode("utf8")

                if not file_name:
                        return None

                file_name = self.get_string( file_name )
                if base_name:
                        return os.path.basename(file_name)
                else:
                        return file_name


        def get_open_file(self,base_name=True):
                sFilter="All Files(*);;Header Files(*.header *.body *.attach *.eml *.txt);;Py Files(*.py *.txt);;Image Files(*.png *.jpg *.bmp);; C++ Files(*.txt *.cpp *.c *.h)"
                file_name=QtGui.QFileDialog.getOpenFileName(self.m_Parent,self.tr("保存文件"),QtCore.QString(""),self.tr(sFilter))
                file_name=unicode(file_name, 'utf8', 'ignore').encode("utf8")

                if not file_name:
                        return None

                file_name = self.get_string( file_name )
                if base_name:
                        return os.path.basename(file_name)
                else:
                        return file_name


        def tableWidget_new_row(self, tblWidget):
                row=tblWidget.rowCount()
                col=tblWidget.columnCount()
                tblWidget.insertRow( row )


        def tableWidget_del_row(self, tblWidget):
                row=tblWidget.currentRow()
                if row<0:
                        row=tblWidget.rowCount()-1
                if row<0:
                        return
                tblWidget.removeRow( row )


        def tableWidget_all_data(self, tblWidget):
                rows=tblWidget.rowCount()
                columns=tblWidget.columnCount()
                rowDict={}

                for i in xrange(rows):
                        columnLst=[]
                        for j in xrange(columns):
                                #QString对象需要使用以下方式转换成python string
                                oNode=tblWidget.item(i,j)
                                if not oNode:
                                        sString=""
                                else:
                                        sString=oNode.text()
                                        sString=unicode(sString, 'utf-8', 'ignore').encode("utf-8")

                                columnLst.append(sString)
                        rowDict[i]=columnLst
                return rowDict


"""
这个类的主要作用是把Combo的可用函数都集中起来展示，方便需要时取用而不用去官网查
"""
class CCombo(CObjectBase):

        def __init__(self, parent):
                super( CCombo, self ).__init__(parent)
                self.combo_obj = QtGui.QComboBox(parent)
                self.combo_obj.SizeAdjustPolicy()
                self.active_cbfunc = None
                self.select_list = []


        def init_select(self, select_list):
                self.select_list = []
                self.combo_obj.clear()
                if not select_list:
                        return
                self.select_list = select_list[:]
                for name in select_list:
                        self.combo_obj.addItem( self.tr(name) )
                self.combo_obj.setCurrentIndex( 0 )


        def get_string(self, code):
                if isinstance(code, QtCore.QString):
                        return unicode(code, 'utf-8', 'ignore').encode("utf-8")
                return get_string( code )


        def get_mainWidget(self):
                return self.combo_obj


        def active_event(self, cb_func=None):
                self.active_cbfunc = cb_func
                self.m_Parent.connect(self.get_mainWidget(), QtCore.SIGNAL('activated(QString)'), self.on_combo_actived )


        def on_combo_actived(self, value):
                if self.active_cbfunc:
                        self.active_cbfunc( value )


        def get_select_text(self):
                text = self.combo_obj.currentText()
                return self.get_string( text )


        def get_select_index(self):
                return self.combo_obj.currentIndex()


        def set_select_by_name(self, value):
                value = self.get_string(value)
                index = self.combo_obj.findText( value )
                self.combo_obj.setCurrentIndex( index )


class CTemplateBase(CObjectBase):

        def __init__(self, parent):
                super( CTemplateBase, self).__init__(parent)
                self.main_Widget = QtGui.QWidget(parent)
                self.main_Layout = None


        def new_label(self, msg):
                obj_label=QtGui.QLabel(self.tr(msg))
                obj_label.setFont(QtGui.QFont('微软雅黑',10))
                return obj_label


        def get_mainWidget(self):
                return self.main_Widget


        def get_mainLayout(self):
                return self.main_Layout


        def init_interface(self):
                pass


        def new_combo(self):
                return CCombo(self.m_Parent)


def init_template():
        import ui_netclient
        import ui_netserver
        import ui_packetset
