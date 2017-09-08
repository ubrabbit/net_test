#coding: utf-8

from gevent import monkey;monkey.patch_all()
import gevent

import sys
import os

from common import *


def init_functions():
    import func_client_tcp
    import func_client_udp
    import func_server

    glist = [
        gevent.spawn( func_client_tcp.start_tcp_listen ),
        gevent.spawn( func_client_udp.start_udp_listen ),
        gevent.spawn( func_server.start_server_listen ),
    ]
    gevent.joinall( glist )
    print "init_functions finish"


def process_quit():
    import func_server

    func_server.process_quit()
