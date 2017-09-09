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
        self.sockfd = None
        self.need_close = False

        self.ip = ip
        self.port = port
        self.client_ip = ""
        self.client_port = "0"
        self.connect_pool = pool.Group()

        self._lock = Semaphore(value=1)
        self.packet_queue = Queue()


    def __repr__(self):
        return "%s:%s"%( self.client_ip, self.client_port )


    def get_log_flag(self):
        return "%s_%s"%(self.idx,self)


    def is_active(self):
        if not self.sockfd or self.sockfd.closed:
            return False
        return True


    def get_idx(self):
        return self.idx


    def get_local_address(self):
        if not self.is_active():
            return "",""
        return self.sockfd.getsockname()


    def do_disconnect(self):
        self.need_close = True
        if self.sockfd and not self.sockfd.closed:
            self.sockfd.close()

        if self.client_ip:
            self.trigger_event( "tcp", "client_disconn", self.client_ip, self.client_port, self )


    def connect_server(self):
        self.notify_console("tcp_client_%s connect start"%(self.idx))

        try:
            conn_succ = False
            with gevent.Timeout(10):
                self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sockfd.connect( (self.ip,self.port) )
                conn_succ = True
        except Exception,err:
            debug_print()

        if conn_succ:
            ip,port = self.get_local_address()
            self.client_ip = ip
            self.client_port = port
            self.notify_console("tcp_client_%s connect succ"%self.get_log_flag())
            self.trigger_event( "tcp", "client_conn", ip, port, self )
        else:
            self.notify_console("tcp_client_%s connect fail"%self.get_log_flag())

        self.connect_pool.spawn( self.connect_send_dispatch )
        self.connect_pool.spawn( self.connect_listen_dispatch )
        self.connect_pool.join()
        self.notify_console("tcp_client_%s connect close"%self.get_log_flag())


    def connect_send_dispatch(self):
        while not self.need_close and self.is_active() and is_process_alive():
            try:
                message = self.packet_queue.get_nowait()
                self.notify_console("tcp_client_%s Send Message '%s'"%(self.get_log_flag(),message))

                message = packet_data( message )
                self._lock.acquire()
                self.notify_console(
                    "tcp_client_%s Send %s bytes to %s:%s"\
                    %(self.get_log_flag(),len(message),self.ip,self.port)
                    )
                self.sockfd.sendall( message )
                self._lock.release()

            except gevent.queue.Empty:
                gevent.sleep(0.01)
            except Exception,e:
                debug_print()
                break
        self.do_disconnect()


    def connect_listen_dispatch(self):
        while not self.need_close and self.is_active() and is_process_alive():
            try:
                data = self.sockfd.recv( RECV_BUFFER_SIZE )
                if not data:
                    break

                message = unpack_data( data )
                self.notify_console(
                    "tcp_client_%s Recv Respond '%s' len=%s bytes"\
                    %( self.get_log_flag(),get_string(message),len(data) )
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
    test_message = "BBB1B2"

    glist = [
        gevent.spawn( start_tcp_listen ),
        gevent.spawn( tcp_send_packet,"202.103.191.47",10037,test_message ),
    ]
    gevent.joinall(glist)

