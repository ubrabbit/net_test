#coding: utf-8

from gevent import monkey;monkey.patch_all()
from gevent import pool
import gevent

import sys
import socket

try:
        from common import *
except Exception,err:
        sys.path.append("../")
        from common import *

RECV_BUFFER_SIZE = 8192

class CUdpContainer(CNotifyObject):

    def __init__(self):
        self.current_idx = 0
        self.connect_pool = pool.Group()


    def init_udp_listen(self):
        def contarner_heart():
            while is_process_alive():
                gevent.sleep( 2 )

        self.connect_pool.spawn( contarner_heart )
        self.connect_pool.join()


    def udp_send_packet(self, ip, port, message):
        global g_client_print

        self.current_idx += 1

        obj_client = CUdpClient( self.current_idx, ip, port )
        obj_client.set_notify_buffer( g_client_print )

        self.connect_pool.spawn( obj_client.udp_send_packet, message )
        if len(self.connect_pool)==1:
            self.connect_pool.join()


class CUdpClient(CNotifyObject):

    def __init__(self, idx, ip, port):
        super(CUdpClient,self).__init__()
        self._sockfd = None
        self.ip = ip
        self.port = port

        self.idx = idx


    def udp_send_packet(self, message):
        address = (self.ip,self.port)
        self._sockfd = socket.socket(type=socket.SOCK_DGRAM)
        self._sockfd.connect(address)

        self.notify_console("udp_client_%s Send Message '%s'"%(self.idx,message))
        message = pack_hex_string( message )
        self.notify_console(
                "udp_client_%s Send %s bytes to %s:%s"\
                %(self.idx,len(message),self.ip,self.port)
                )
        self._sockfd.sendall(message)
        data, address = self._sockfd.recvfrom( RECV_BUFFER_SIZE )
        self.notify_console(
                "udp_client_%s Recv Respond '%s' len=%s bytes"\
                %(self.idx, get_string(data), len(data))
                )


def reset_buffer( obj_fileEditor ):
    global g_udp_container
    global g_client_print
    g_client_print = obj_fileEditor

    g_udp_container.set_notify_buffer( obj_fileEditor )


def start_udp_listen():
    global g_udp_container
    g_udp_container.init_udp_listen()


def udp_send_packet( ip, port, message ):
    global g_udp_container
    g_udp_container.udp_send_packet( ip, port, message )


if not globals().has_key("g_udp_container"):
    global g_udp_container
    g_udp_container = CUdpContainer()


if not globals().has_key("g_client_print"):
    global g_client_print
    g_client_print = None


if __name__ == "__main__":
    udp_send_packet("127.0.0.1",10002,"BCDF")
    udp_send_packet("127.0.0.1",10002,"DDDD")
