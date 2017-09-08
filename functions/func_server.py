#coding: utf-8

from gevent import monkey;monkey.patch_all()
from gevent.server import StreamServer
from gevent.server import DatagramServer
from gevent import pool
import gevent

import sys
import socket

try:
        from common import *
except Exception,err:
        sys.path.append("../")
        from common import *


class CServerContainer( object ):


    def __init__(self):
        self.server_tcp = None
        self.server_udp = None
        self.connect_pool = pool.Group()


    def init_server_listen(self):
        def contarner_heart():
            while True:
                gevent.sleep( 60 )

        self.connect_pool.spawn( contarner_heart )
        self.connect_pool.join()


    def start_tcp_server(self, ip, port):
        obj_server = CTcpServer()
        self.server_tcp = obj_server
        self.connect_pool.spawn( obj_server.start_server, ip, port )


    def start_udp_server(self, ip, port):
        obj_server = CUdpServer( "%s:%s"%(ip,port) )

        self.server_udp = obj_server
        self.connect_pool.spawn( obj_server.serve_forever )


class CTcpServer( object ):

    def start_server(self, ip, port):
        obj_server = StreamServer( (ip, port), self.client_connect_tcp )
        obj_server.serve_forever()


    @staticmethod
    def client_connect_tcp(sockfd, address):
            _ip, _port = address
            notify_console("New Connect From %s:%s"%(_ip, _port))
            while True:
                message = sockfd.recv( 10240 )
                if not message:
                        break
                print_empty(2)

                str_list = unpack_hex_string(message)
                notify_console(
                        "tcp_server recv from: %s:%s data: '%s' len: %s bytes"\
                        %(get_string(_ip),get_string(_port), get_string(str_list),len(message))
                        )

                message = "".join( list(str_list) )
                notify_console("server respond: '%s'"%message)
                sockfd.sendall( message )

            notify_console("Connect From %s:%s Closed"%(_ip, _port))
            try:
                    sockfd.shutdown(socket.SHUT_WR)
            except Exception,e:
                    print e
            finally:
                    sockfd.close()


class CUdpServer( DatagramServer ):

    def handle(self, message, address):
        _ip, _port = address
        print_empty(2)

        str_list = unpack_hex_string(message)
        notify_console("udp_server recv from %s:%s data: '%s' len: %s bytes"%(_ip,_port, get_string(str_list), len(message) ))

        message = "".join( list(str_list) )
        notify_console("server respond: '%s'"%message)
        self.socket.sendto(message, address)


def start_tcp_server(ip="127.0.0.1",port=10001):
    global g_server_container
    g_server_container.start_tcp_server( ip, port )


def start_udp_server(ip="127.0.0.1",port=10002):
    global g_server_container
    g_server_container.start_udp_server( ip, port )


def start_server_listen():
    global g_server_container

    g_server_container.init_server_listen()


if not globals().has_key("g_server_container"):
    global g_server_container
    g_server_container = CServerContainer()


if __name__ == "__main__":

    glist = [
        gevent.spawn( start_server_listen ),
        gevent.spawn( start_tcp_server ),
        gevent.spawn( start_udp_server ),
    ]
    gevent.joinall(glist)
