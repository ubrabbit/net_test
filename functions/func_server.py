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
                notify_console(
                        "tcp_server recv from: %s:%s data: '%s' len: %s bytes"\
                        %(get_string(_ip),get_string(_port), get_string(message),len(message))
                        )

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
        notify_console("udp_server recv from %s:%s data: '%s' len: %s bytes"%(_ip,_port, get_string(message), len(message) ))

        notify_console("server respond: '%s'"%message)
        self.socket.sendto(message, address)


def start_server_tcp(ip="127.0.0.1",port=10001):
    obj_server = CTcpServer()
    obj_server.start_server( ip, port )


def start_server_udp(ip="127.0.0.1",port=10002):
    obj_server = CUdpServer( "%s:%s"%(ip,port) )
    obj_server.serve_forever()

#start_server_udp()
start_server_tcp()
