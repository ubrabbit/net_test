#coding: utf-8

"""
"""

import sys
import os
import copy
import math
import re

from PyQt4 import QtCore, QtGui

from common import *

import interface
import exec_test

#显示中文
QtCore.QTextCodec.setCodecForTr(QtCore.QTextCodec.codecForName("utf8"))
QtCore.QTextCodec.setCodecForCStrings(QtCore.QTextCodec.codecForName("utf8"))
QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("system"))


def main():
        init_runpath()

        interface.init_interface()


if __name__ == "__main__":
        main()
