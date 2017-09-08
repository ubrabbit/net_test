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


class CTcpContainer(CNotifyObject):

    def __init__(self):
        self.current_idx = 0
        self.client_list = {}
        self.connect_pool = pool.Group()


    def init_tcp_listen(self):
        def contarner_heart():
            while is_process_alive():
                gevent.sleep( 2 )

        self.connect_pool.spawn( contarner_heart )
        self.connect_pool.join()


    def new_connect(self, ip, port):
        global g_client_print

        self.current_idx += 1

        obj_client = CTcpClient( self.current_idx, ip, port )
        obj_client.set_notify_buffer( g_client_print )

        self.client_list[ self.current_idx ] = obj_client
        self.connect_pool.spawn( obj_client.connect_server )

        return obj_client


    def get_connect(self, idx):
        return self.client_list[ idx ]


class CTcpClient(CNotifyObject):

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


    def is_active(self):
        if not self._sockfd or self._sockfd.closed:
            return False
        return True


    def get_idx(self):
        return self.idx


    def do_disconnect(self):
        self._need_close = True
        if self._sockfd and not self._sockfd.closed:
            self._sockfd.close()


    def connect_server(self):
        self.notify_console("tcp_client_%s connect start"%self.idx)

        with gevent.Timeout(15):
            self._sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sockfd.connect( (self.ip,self.port) )

        self.notify_console("tcp_client_%s connect succ"%self.idx)
        self.connect_pool.spawn( self.connect_send_dispatch )
        self.connect_pool.spawn( self.connect_listen_dispatch )
        self.connect_pool.join()
        self.notify_console("tcp_client_%s connect close"%self.idx)


    def connect_send_dispatch(self):
        while not self._need_close and self.is_active() and is_process_alive():
            try:
                message = self.packet_queue.get_nowait()
                message = pack_hex_string( message )

                self._lock.acquire()

                self.notify_console("tcp_client_%s Send Message '%s'"%(self.idx,message))
                self.notify_console(
                    "tcp_client_%s Send %s bytes to %s:%s"\
                    %(self.idx,len(message),self.ip,self.port)
                    )
                self._sockfd.sendall( message )
                self._lock.release()

            except gevent.queue.Empty:
                gevent.sleep(0.01)
            except Exception,e:
                debug_print()
                break
        self.do_disconnect()


    def connect_listen_dispatch(self):
        while not self._need_close and self.is_active() and is_process_alive():
            try:
                message = self._sockfd.recv( RECV_BUFFER_SIZE )
                if not message:
                    break
                self.notify_console(
                    "tcp_client_%s Recv Respond '%s' len=%s bytes"\
                    %( self.idx,get_string(message),len(message) )
                    )
            except Exception,e:
                debug_print()
                break
        self.do_disconnect()


    def tcp_send_packet(self, message):
        self.packet_queue.put_nowait( message )


def reset_buffer( obj_fileEditor ):
    global g_tcp_container
    global g_client_print
    g_client_print = obj_fileEditor

    g_tcp_container.set_notify_buffer( obj_fileEditor )


def start_tcp_listen():
    global g_tcp_container
    g_tcp_container.init_tcp_listen()


def tcp_new_connect( ip, port ):
    global g_tcp_container
    client_obj = g_tcp_container.new_connect( ip, port )
    return client_obj


def tcp_send_packet(ip, port, message, idx=0):
    global g_tcp_container

    if idx <= 0:
        client_obj = g_tcp_container.new_connect( ip, port )
    else:
        client_obj = g_tcp_container.get_connect( idx )
    client_obj.tcp_send_packet( message )
    return client_obj


if not globals().has_key("g_tcp_container"):
    global g_tcp_container
    g_tcp_container = CTcpContainer()

if not globals().has_key("g_client_print"):
    global g_client_print
    g_client_print = None


if __name__ == "__main__":
    test_message = pack_hex_string("BBB1B2")

    glist = [
        gevent.spawn( start_tcp_listen ),
        gevent.spawn( tcp_send_packet,"127.0.0.1",10001,test_message ),
    ]
    gevent.joinall(glist)

