#coding: utf-8

from gevent import monkey;monkey.patch_all()
from gevent.server import StreamServer
from gevent.server import DatagramServer
from gevent import pool
from gevent.queue import Queue
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
        super( CServerContainer, self ).__init__()
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
        return obj_server


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
        return obj_server


class CConnUnit( CNotifyObject ):

    def __init__(self, sockfd, proto, ip, port):
        super(CConnUnit,self).__init__()
        global g_server_print

        self.proto = proto
        self.ip = ip
        self.port = port
        self.packet_queue = Queue()
        self.task_pool = pool.Group()
        self.sockfd = sockfd

        self.need_close = False

        self.set_notify_buffer( g_server_print )


    def __repr__(self):
        return "%s:%s"%(self.ip,self.port)


    def is_active(self):
        if not is_process_alive():
            return False
        if self.need_close:
            return False
        if not self.sockfd or self.sockfd.closed:
            return False
        return True


    def tcp_client_dispatch(self):
        self.task_pool.spawn( self.tcp_recv_dispatch )
        self.task_pool.spawn( self.tcp_send_dispatch )
        self.task_pool.join()


    def tcp_recv_dispatch(self):
        self.on_new_connect()
        while self.is_active():
            try:
                with gevent.Timeout(3):
                    message = self.sockfd.recv( 10240 )
                    if not message:
                            break

                print_empty(2)
                str_list = unpack_data(message)
                self.notify_console(
                        "tcp_server recv from: %s data: '%s' len: %s bytes"\
                        %(get_string(self),get_string(str_list),len(message))
                        )

                self.on_recv_packet( message )
                #message = "".join( list(str_list) )
                #self.notify_console("server respond: '%s'"%message)
                #sockfd.sendall( message )
            except gevent.Timeout:
                gevent.sleep(0.001)
            except Exception,e:
                debug_print()
                break

        self.need_close = True
        self.on_disconnect()
        try:
                self.sockfd.shutdown(socket.SHUT_WR)
        except Exception,e:
                print e
        finally:
                self.sockfd.close()


    def tcp_send_dispatch(self):
        while self.is_active():
            try:
                message = self.packet_queue.get_nowait()
                self.sockfd.sendall( message )
            except gevent.queue.Empty:
                gevent.sleep(0.001)
            except Exception,e:
                debug_print()
                break
        self.need_close = True


    def udp_client_dispatch(self, message):
        self.on_new_connect()
        str_list = unpack_data(message)
        print_empty(2)
        self.notify_console("udp_server recv from %s data: '%s' len: %s bytes"%(self, get_string(str_list), len(message) ))
        self.on_recv_packet( message )
        self.on_disconnect()


    def send_packet(self, message):
        message = packet_data( message )
        if self.proto == "tcp":
            self.packet_queue.put_nowait( message )
        else:
            self.sockfd.sendto(message, (self.ip,self.port))


    def on_new_connect(self):
        trigger_event( self.proto, "connect", self )


    def on_disconnect(self):
        trigger_event( self.proto, "disconnect", self )


    def on_recv_packet(self, message ):
        trigger_event( self.proto, "packet", self, message )


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


    def client_connect_tcp(self, sockfd, address):
            _ip, _port = address
            self.notify_console("New Connect From %s:%s"%(_ip, _port))

            obj_conn = CConnUnit(sockfd,"tcp",_ip,_port)
            obj_conn.tcp_client_dispatch()

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
        try:
            obj_conn = CConnUnit(self.socket,"udp",_ip,_port)
            obj_conn.udp_client_dispatch( message )
        except Exception,err:
            debug_print()

        #self.notify_console("server respond: '%s'"%message)
        #self.socket.sendto(message, address)


def regist_event( proto, event_name, func_key, funcobj ):
    global g_event_callback
    g_event_callback.setdefault( proto, {} )
    g_event_callback[proto].setdefault( event_name, {} )
    g_event_callback[proto][event_name][func_key] = funcobj


def trigger_event( proto, event_name, *param ):
    global g_event_callback
    if not proto in g_event_callback:
        return False
    if not event_name in g_event_callback[proto]:
        return False
    for func_key in g_event_callback[proto][event_name].keys():
        funcobj = g_event_callback[proto][event_name][func_key]
        safe_call( funcobj, *param )
    return True


def reset_buffer( obj_fileEditor ):
    global g_server_container
    global g_server_print
    g_server_print = obj_fileEditor

    g_server_container.set_notify_buffer( obj_fileEditor )


def start_tcp_server(ip="127.0.0.1",port=10001):
    global g_server_container
    return g_server_container.start_tcp_server( ip, port )


def start_udp_server(ip="127.0.0.1",port=10002):
    global g_server_container
    return g_server_container.start_udp_server( ip, port )


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


if not globals().has_key("g_event_callback"):
    global g_event_callback
    g_event_callback = {}


if __name__ == "__main__":

    glist = [
        gevent.spawn( start_server_listen ),
        gevent.spawn( start_tcp_server ),
        gevent.spawn( start_udp_server ),
    ]
    gevent.joinall(glist)
