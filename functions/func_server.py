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


class CServerContainer( CNotifyObject ):


    def __init__(self):
        self.server_tcp = None
        self.server_udp = None
        self.connect_pool = pool.Group()


    def init_server_listen(self):
        def contarner_heart():
            while is_process_alive():
                gevent.sleep( 2 )

        self.connect_pool.spawn( contarner_heart )
        self.connect_pool.join()


    def process_quit(self):
        self.connect_pool.kill()


    def start_tcp_server(self, ip, port):
        global g_server_print
        self.notify_console("start_tcp_server: %s:%s"%( ip,port))

        if self.server_tcp:
            self.server_tcp.close()

        port = int(port)
        obj_server = CTcpServer()
        obj_server.set_notify_buffer( g_server_print )

        self.server_tcp = obj_server
        self.connect_pool.spawn( obj_server.start_server, ip, port )


    def start_udp_server(self, ip, port):
        global g_server_print
        self.notify_console("start_udp_server: %s:%s"%( ip,port))

        if self.server_udp:
            self.server_udp.close()

        port = int(port)
        obj_server = CUdpServer( "%s:%s"%(ip,port) )
        obj_server.set_notify_buffer( g_server_print )

        self.server_udp = obj_server
        self.connect_pool.spawn( obj_server.serve_forever )


class CTcpServer( CNotifyObject ):

    def close(self):
        obj_server = getattr(self, "obj_server", None)
        if obj_server:
            obj_server.close()
            delattr(self,"obj_server")


    def start_server(self, ip, port):
        port = int(port)
        self.obj_server = StreamServer( (ip, port), self.client_connect_tcp )
        self.obj_server.serve_forever()


    @staticmethod
    def client_connect_tcp(sockfd, address):
            _ip, _port = address
            self.notify_console("New Connect From %s:%s"%(_ip, _port))
            while True:
                message = sockfd.recv( 10240 )
                if not message:
                        break
                print_empty(2)

                str_list = unpack_hex_string(message)
                self.notify_console(
                        "tcp_server recv from: %s:%s data: '%s' len: %s bytes"\
                        %(get_string(_ip),get_string(_port), get_string(str_list),len(message))
                        )

                message = "".join( list(str_list) )
                self.notify_console("server respond: '%s'"%message)
                sockfd.sendall( message )

            self.notify_console("Connect From %s:%s Closed"%(_ip, _port))
            try:
                    sockfd.shutdown(socket.SHUT_WR)
            except Exception,e:
                    print e
            finally:
                    sockfd.close()


class CUdpServer( DatagramServer, CNotifyObject ):

    def handle(self, message, address):
        _ip, _port = address
        print_empty(2)

        str_list = unpack_hex_string(message)
        self.notify_console("udp_server recv from %s:%s data: '%s' len: %s bytes"%(_ip,_port, get_string(str_list), len(message) ))

        message = "".join( list(str_list) )
        self.notify_console("server respond: '%s'"%message)
        self.socket.sendto(message, address)


def reset_buffer( obj_fileEditor ):
    global g_server_container
    global g_server_print
    g_server_print = obj_fileEditor

    g_server_container.set_notify_buffer( obj_fileEditor )


def start_tcp_server(ip="127.0.0.1",port=10001):
    global g_server_container
    g_server_container.start_tcp_server( ip, port )


def start_udp_server(ip="127.0.0.1",port=10002):
    global g_server_container
    g_server_container.start_udp_server( ip, port )


def start_server_listen():
    global g_server_container
    g_server_container.init_server_listen()


def process_quit():
    global g_server_container
    g_server_container.process_quit()


if not globals().has_key("g_server_container"):
    global g_server_container
    g_server_container = CServerContainer()


if not globals().has_key("g_server_print"):
    global g_server_print
    g_server_print = None


if __name__ == "__main__":

    glist = [
        gevent.spawn( start_server_listen ),
        gevent.spawn( start_tcp_server ),
        gevent.spawn( start_udp_server ),
    ]
    gevent.joinall(glist)
