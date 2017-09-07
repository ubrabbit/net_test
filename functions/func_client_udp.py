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

class CUdpContainer(object):

    def __init__(self):
        self.current_idx = 0
        self.connect_pool = pool.Group()


    def init_udp_listen(self):
        def contarner_heart():
            while True:
                gevent.sleep( 60 )

        self.connect_pool.spawn( contarner_heart )
        self.connect_pool.join()


    def udp_send_packet(self, ip, port, message):
        self.current_idx += 1

        obj_client = CUdpClient( self.current_idx, ip, port )
        self.connect_pool.spawn( obj_client.udp_send_packet, message )
        if len(self.connect_pool)==1:
            self.connect_pool.join()


class CUdpClient(object):

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

        message = pack_hex_string( message )
        notify_console(
                "udp_client_%s Send '%s' len=%s bytes to %s:%s"\
                %(self.idx, get_string(message),len(message),self.ip,self.port)
                )
        self._sockfd.sendall(message)
        data, address = self._sockfd.recvfrom( RECV_BUFFER_SIZE )
        notify_console(
                "udp_client_%s Recv Respond '%s' len=%s bytes"\
                %(self.idx, get_string(data), len(data))
                )


def start_udp_listen():
    global g_udp_container
    g_udp_container.init_udp_listen()


def udp_send_packet( ip, port, message ):
    global g_udp_container
    g_udp_container.udp_send_packet( ip, port, message )


if not globals().has_key("g_udp_container"):
    global g_udp_container
    g_udp_container = CUdpContainer()


if __name__ == "__main__":
    udp_send_packet("127.0.0.1",10002,"BCDF")
    udp_send_packet("127.0.0.1",10002,"DDDD")
