#coding: utf-8

"""
"""
from gevent import monkey;monkey.patch_all()
from gevent import pool
import gevent

import sys
import copy
import math
import re

import traceback
from functools import partial

from PyQt4 import QtCore, QtGui

from common import *
import console_log

import functions
import ui_template


#显示中文
QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf8"))
QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForName("utf8"))
QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("system"))


DEFINE_REDIRECT_STDOUT = 1


class CApp(QtGui.QMainWindow):

        def __init__(self):
                QtGui.QMainWindow.__init__(self)

                self.m_Interface=CInterface(self)
                self.setWindowTitle(self.tr("NET测试工具"))

                screen = QtGui.QDesktopWidget().screenGeometry()
                self.resize( 800 , 800 )


        def __del__(self):
                console_log.Console_Free()

        def GetAbout(self):
                sCode=\
"""
作者：ouba
版本：%s
这是一个小工具
"""%self.GetVersion()
                return sCode


        def GetVersion(self):
                return "v0.01"


        def info(self, title, msg):
                QtGui.QMessageBox.information(self, self.tr(title), self.tr(msg))


        def critical(self, title, msg):
                QtGui.QMessageBox.critical(self, self.tr(title), self.tr(msg))


        def warning(self, title, msg):
                iFlag=QtGui.QMessageBox.Save|QtGui.QMessageBox.Discard|QtGui.QMessageBox.Cancel
                button=QtGui.QMessageBox.warning(self,title,self.tr("msg"),iFlag,QtGui.QMessageBox.Save)
                if button==QtGui.QMessageBox.Save:
                        pass
                elif button==QtGui.QMessageBox.Discard:
                        pass
                elif button==QtGui.QMessageBox.Cancel:
                        return


class CInterface(object):

        def __init__(self, parent):
                super( CInterface, self).__init__()
                self.m_Parent = parent
                self.console_Edit, self.log_Edit = None, None
                try:
                        self.Layout_Init()
                        self.StatusBar_Init()

                        self.Signal_Init()
                except Exception,e:
                        console_log.Console_Free()
                        traceback.print_exc()
                        logerror( get_exception_info() )
                        exit(-1)


        def tr(self,msg):
                return self.m_Parent.tr(msg)


        def info(self, title, msg):
                self.m_Parent.info(title,msg)


        def critical(self, title, msg):
                self.m_Parent.critical(title,msg)


        def warning(self, title, msg):
                self.m_Parent.warning(title,msg)


        def Layout_Init(self):
                centralWidget=QtGui.QWidget(self.m_Parent)
                self.m_Parent.setCentralWidget(centralWidget)

                self.tabWidget_main=QtGui.QTabWidget(self.m_Parent)
                self.mainLayout=QtGui.QHBoxLayout(centralWidget)

                self.listWidget_main=QtGui.QListWidget()
                self.graphStack_main=QtGui.QStackedWidget()

                self.listWidget_main.insertItem(0,self.m_Parent.tr("说明"))
                self.m_Parent.connect(self.listWidget_main,QtCore.SIGNAL("currentRowChanged(int)"),self.graphStack_main,QtCore.SLOT("setCurrentIndex(int)"))

                self.mainLayout.addWidget(self.listWidget_main)
                self.mainLayout.addWidget(self.tabWidget_main)
                #设置布局空间的比例
                self.mainLayout.setStretchFactor(self.listWidget_main,1)
                self.mainLayout.setStretchFactor(self.tabWidget_main,29)

                self.tabWidget_main.addTab(self.graphStack_main,self.m_Parent.tr("界面"))

                if DEFINE_REDIRECT_STDOUT:
                        self.console_Edit,self.log_Edit=console_log.Console_Init(self)
                        self.tabWidget_main.addTab(self.console_Edit,self.m_Parent.tr("控制台"))
                        self.tabWidget_main.addTab(self.log_Edit,self.m_Parent.tr("日志"))
                else:
                        console_Edit=QtGui.QTextEdit()
                        log_Edit=QtGui.QTextEdit()
                        self.console_Edit,self.log_Edit=console_Edit,log_Edit

                #--------------------- 各个子界面的初始化
                self.Instruction_Init()

                self.listWidget_main.insertItem(1,self.m_Parent.tr("客户端"))
                self.listWidget_main.insertItem(2,self.m_Parent.tr("服务器"))

                self.graphStack_main.addWidget( ui_template.ui_netclient.init_template(self.m_Parent) )
                self.graphStack_main.addWidget( ui_template.ui_netserver.init_template(self.m_Parent) )


        def StatusBar_Init(self):
                menubar=self.m_Parent.menuBar()
                helpMenu=menubar.addMenu(self.m_Parent.tr("帮助"))

                self.m_Parent.statusBar()

                #QtGui.QAction是关于菜单栏、工具栏或自定义快捷键动作的抽象。
                exitAction=QtGui.QAction(QtGui.QIcon(""),self.m_Parent.tr("退出"),self.m_Parent)
                #定义快捷键。
                exitAction.setShortcut("Ctrl+Q")
                #当鼠标停留在菜单上时，在状态栏显示该菜单的相关信息。
                exitAction.setStatusTip(self.m_Parent.tr("Ctrl+Q 退出程序"))
                #选定特定的动作，发出触发信号。该信号与QtGui.QApplication部件的quit()方法
                #相关联，这将会终止应用程序。
                exitAction.triggered.connect(QtGui.qApp.quit)

                helpAction=QtGui.QAction(QtGui.QIcon(""),self.m_Parent.tr("说明"),self.m_Parent)
                helpAction.setShortcut("Ctrl+H")
                helpAction.setStatusTip(self.m_Parent.tr("弹出帮助窗口"))
                helpAction.triggered.connect(self.m_Parent.GetAbout)

                aboutAction=QtGui.QAction(QtGui.QIcon(""),self.m_Parent.tr("关于"),self.m_Parent)
                aboutAction.setStatusTip(self.m_Parent.tr("程序版本和作者信息"))
                aboutAction.triggered.connect(self.m_Parent.GetAbout)

                helpMenu.addAction(helpAction)
                helpMenu.addAction(aboutAction)

                toolBar=self.m_Parent.addToolBar(self.m_Parent.tr(""))
                toolBar.addAction(exitAction)


        def Signal_Init(self):
                pass


        def Instruction_Init(self):
                tipWidget=QtGui.QWidget(self.m_Parent)
                layout_Vertical=QtGui.QVBoxLayout(tipWidget)
                layout_Horizon=QtGui.QHBoxLayout()
                tips=QtGui.QTextEdit()
                sText=self.m_Parent.GetAbout()
                tips.setText(self.m_Parent.tr(sText))
                tips.setEnabled(False)
                layout_Vertical.addWidget(tips)
                layout_Vertical.addLayout(layout_Horizon)
                layout_Vertical.addStretch(5)

                self.graphStack_main.addWidget(tipWidget)


def mainloop(app):
    while True:
        app.processEvents()
        while app.hasPendingEvents():
            app.processEvents()
            gevent.sleep(0)
        gevent.sleep(0) # don't appear to get here but cooperate again


def testprint():
    print 'this is running'
    gevent.spawn_later(30, testprint)


def init_interface():
        ui_template.init_template()

        app = QtGui.QApplication([])
        window = CApp()
        window.show()
        app.installEventFilter(window)

        glist = [
                gevent.spawn( functions.init_functions ),
                #gevent.spawn( testprint ),
                gevent.spawn( mainloop, app ),
        ]
        gevent.joinall( glist )
        #sys.exit(app.exec_())


if __name__ == "__main__":
        init_runpath()
        init_interface()
