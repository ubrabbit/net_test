#coding: utf-8

"""
/*
 *  Copyright (C) 2011-2017 ubrabbit
 *  Author: ubrabbit <ubrabbit@gmail.com>
 *  Date: 2017-06-16 12:46:11
 *
 */

 """

from PyQt4 import QtCore,QtGui
from functools import partial

import sys


def Console_Init(window):
        console_Edit=QtGui.QTextEdit()
        log_Edit=QtGui.QTextEdit()
        console_Edit.setReadOnly(True)
        log_Edit.setReadOnly(True)

        cb_stdout=partial(Stdout_Output,console_Edit)
        cb_stderr=partial(Stderr_Output,log_Edit)

        sys.stdout=EmittingStream(textWritten=cb_stdout)
        sys.stderr=EmittingStream(textWritten=cb_stderr)

        return console_Edit,log_Edit


def Console_Free():
        sys.stdout=sys.__stdout__
        sys.stderr=sys.__stderr__


#回调不能出现 print ，不然就无限递归了
def Stdout_Output(console_Edit,text):
        cursor=console_Edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        console_Edit.setTextCursor(cursor)
        console_Edit.ensureCursorVisible()


def Stderr_Output(log_Edit,text):
        cursor=log_Edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        log_Edit.setTextCursor(cursor)
        log_Edit.ensureCursorVisible()


class EmittingStream(QtCore.QObject):

        textWritten=QtCore.pyqtSignal(str)

        def write(self,text):
                #emit：发射信号
                self.textWritten.emit(str(text))

