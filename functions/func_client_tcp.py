#coding: utf-8

from gevent import monkey;monkey.patch_all()
from gevent import pool
from gevent.lock import Semaphore
from gevent.queue import Queue
import gevent

import sys
import socket
import argparse

try:
        from common import *
except Exception,err:
        sys.path.append("../")
        from common import *


RECV_BUFFER_SIZE = 8192


class CTcpContainer(object):

    def __init__(self):
        self.current_idx = 0
        self.client_list = {}
        self.connect_pool = pool.Group()


    def init_tcp_listen(self):
        def contarner_heart():
            while True:
                gevent.sleep( 60 )

        self.connect_pool.spawn( contarner_heart )
        self.connect_pool.join()


    def new_connect(self, ip, port):
        self.current_idx += 1

        obj_client = CTcpClient( self.current_idx, ip, port )
        self.client_list[ self.current_idx ] = obj_client
        self.connect_pool.spawn( obj_client.connect_server )
        if len(self.connect_pool)==1:
            self.connect_pool.join()
        return obj_client


    def get_connect(self, idx):
        return self.client_list[ idx ]


class CTcpClient(object):

    def __init__(self, idx, ip, port):
        super(CTcpClient,self).__init__()
        self.idx = idx
        self._sockfd = None
        self._need_close = False

        self.ip = ip
        self.port = port
        self.connect_pool = pool.Group()

        self._lock = Semaphore(value=1)
        self.packet_queue = Queue()


    def _is_active(self):
        if not self._sockfd or self._sockfd.closed:
            return False
        return True


    def _do_disconnect(self):
        self._need_close = True
        if self._sockfd and not self._sockfd.closed:
            self._sockfd.close()


    def connect_server(self):
        self._sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sockfd.connect( (self.ip,self.port) )

        notify_console("tcp_client_%s connect start"%self.idx)
        self.connect_pool.spawn( self.connect_send_dispatch )
        self.connect_pool.spawn( self.connect_listen_dispatch )
        self.connect_pool.join()
        notify_console("tcp_client_%s connect close"%self.idx)


    def connect_send_dispatch(self):
        while not self._need_close and self._is_active():
            try:
                message = self.packet_queue.get_nowait()

                self._lock.acquire()
                notify_console(
                    "tcp_client_%s Send message '%s' len=%s bytes to %s:%s"\
                    %(self.idx,get_string(message),len(message),self.ip,self.port)
                    )
                self._sockfd.sendall( message )
                self._lock.release()

            except gevent.queue.Empty:
                gevent.sleep(0.01)
            except Exception,e:
                debug_print()
                break
        self._do_disconnect()


    def connect_listen_dispatch(self):
        while not self._need_close and self._is_active():
            try:
                message = self._sockfd.recv( RECV_BUFFER_SIZE )
                if not message:
                    break
                notify_console(
                    "tcp_client_%s Recv Respond '%s' len=%s bytes"\
                    %( self.idx,get_string(message),len(message) )
                    )
            except Exception,e:
                debug_print()
                break
        self._do_disconnect()


    def tcp_send_packet(self, message):
        self.packet_queue.put_nowait( message )


def start_tcp_listen():
    global g_tcp_container
    g_tcp_container.init_tcp_listen()


def tcp_send_packet(message, ip, port, idx=0):
    global g_tcp_container

    if idx <= 0:
        client_obj = g_tcp_container.new_connect( ip, port )
    else:
        client_obj = g_tcp_container.get_connect( idx )
    client_obj.tcp_send_packet( message )


if not globals().has_key("g_tcp_container"):
    global g_tcp_container
    g_tcp_container = CTcpContainer()


test_message = pack_hex_string("BBB1B2")

glist = [
    gevent.spawn( start_tcp_listen ),
    gevent.spawn( tcp_send_packet, test_message,"127.0.0.1",10001 ),
]
gevent.joinall(glist)

