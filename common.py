#coding:utf-8

import sys
import os
import hashlib
import random

import chardet
import time
import traceback
import ConfigParser

from functools import partial

import logging
from logging.handlers import TimedRotatingFileHandler


def get_md5_value(src):
        myMd5 = hashlib.md5()
        myMd5.update(src)
        myMd5_Digest = myMd5.hexdigest()
        return myMd5_Digest


def singleton_cls(cls, *args, **kw):
        instances = {}
        def _singleton(*args, **kw):
                if cls not in instances:
                        instances[cls] = cls(*args, **kw)
                return instances[cls]
        return _singleton


def safe_call(funcobj, *param):
    rtn = None
    try:
        rtn = funcobj(*param)
    except Exception,err:
        rtn = -1
        debug_print()
    return rtn


# 递归创建路径
def recursion_make_dir(path, permit=0755) :
        import os
        path = path.replace("\\","/")
        if os.path.exists(path) : return False
        os.makedirs(path)
        os.chmod(path, permit)
        return True


# 转换字符串为 unicode
def get_unicode(code) :
        code_type = type(code)
        if code_type.__name__ == 'unicode' :
                return code
        charset = chardet.detect(code)['encoding']
        if not charset:
            return code.decode("utf-8","ignore")
        return code.decode(charset)


def get_string(code):
        if isinstance(code, unicode):
                return code.encode("utf-8","ignore")
        code=get_unicode(str(code))
        return code.encode("utf-8","ignore")


# 获取异常信息
def get_exception_info() :
        lines = []
        for line in traceback.format_exc().strip().split('\n') : lines.append('  > ' + line)

        err_msg = '\n'.join(lines)
        return get_string(err_msg)


def debug_print():
        traceback.print_exc()


def debug_notify(msg):
        print msg


def partial_functor(func, *param):
        return partial(func, *param)


#全局对象，单例
@singleton_cls
class CGlobalConfig(object):

        def __init__(self):
                self.all_logger_list = {}
                self.obj_container = {}


        def get_logger(self, logger_name):
            if not logger_name in self.all_logger_list:
                    logFilePath = "%s/%s.log"%(get_logpath(),logger_name)
                    obj_log = logging.getLogger(logger_name)
                    obj_log.setLevel(logging.INFO)
                    handler = TimedRotatingFileHandler(logFilePath,
                                       when="d",
                                       interval=1,
                                       backupCount=7)
                    obj_log.addHandler(handler)
                    self.all_logger_list[ logger_name ] = obj_log
            else:
                    obj_log = self.all_logger_list[ logger_name ]

            return obj_log


        def add_container_obj(self, key, obj):
                self.obj_container[ key ] = obj


        def get_container_obj(self, key):
                return self.obj_container.get(key, None)


def logfile(file_name, msg):
        file_name = get_string(file_name)
        msg = get_string(msg)

        time_info=time.strftime('%Y-%m-%d %H:%M:%S')
        msg="[%s] %s"%(time_info,msg)

        obj_global = get_config_obj()
        obj_log = obj_global.get_logger( file_name )
        obj_log.info( msg )

        print msg


def logerror(msg):
        msg = get_string(msg)

        time_info=time.strftime('%Y-%m-%d %H:%M:%S')
        msg="[%s] %s"%(time_info,msg)

        file_name = "error"

        obj_global = get_config_obj()
        obj_log = obj_global.get_logger( file_name )
        obj_log.info( msg )

        print msg


def get_filepath(file_path):
        platform = sys.platform
        #linux是utf-8
        if platform.startswith("linux"):
                return get_string(get_unicode(file_path))
        #win是gbk
        elif platform.startswith("win"):
                return get_unicode(file_path).encode("gbk","ignore")
        return file_path


def get_parent_folder(self, cur_path):
        parent_path = os.path.dirname(os.getcwd())
        parent_path = parent_path.replace("\\","/")
        if parent_path.endswith("/"):
                parent_path = parent_path[:-1]
        parent_folder = parent_path.split("/")[-1]
        return parent_folder


def init_runpath():
        sys.path.append("functions")
        sys.path.append("unittest")

        cur_path = os.getcwd()
        if cur_path.endswith("functions") or cur_path.endswith("functions/"):
                cur_path = os.path.dirname(os.getcwd())  #取当前目录上一级目录
        elif cur_path.endswith("unittest") or cur_path.endswith("unittest/"):
                cur_path = os.path.dirname(os.getcwd())
        print ">>>>>>>>>>>>     ",cur_path

        obj_cfg = get_config_obj()
        obj_cfg.PROCESS_RUN_PATH = cur_path

        log_path = "%s/log"%cur_path
        cache_path = "%s/cache"%cur_path

        recursion_make_dir( log_path )
        recursion_make_dir( cache_path )

        obj_cfg.PROCESS_LOG_PATH = log_path
        obj_cfg.PROCESS_CACHE_PATH = cache_path


def get_runpath():
        obj_cfg = get_config_obj()
        return obj_cfg.PROCESS_RUN_PATH


def get_cachepath():
        obj_cfg = get_config_obj()
        return obj_cfg.PROCESS_CACHE_PATH


def get_logpath():
        obj_cfg = get_config_obj()
        return obj_cfg.PROCESS_LOG_PATH


def get_config_obj():
        if not "g_global_config" in globals():
                global g_global_config
                g_global_config = CGlobalConfig()

                init_runpath()
        return g_global_config


def get_container_obj(name):
        obj_cfg = get_config_obj()
        return obj_cfg.get_container_obj(name)


def notify_console(msg):
        platform = sys.platform
        #linux是utf-8
        if platform.startswith("linux"):
                msg = get_string(get_unicode(msg))
        #win是gbk
        elif platform.startswith("win"):
                msg = get_unicode(msg).encode("gbk","ignore")
        print msg


def print_empty(line_cnt=1):
        for i in xrange(line_cnt):
                print ""
