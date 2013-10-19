#!/usr/bin/env python

"""ash connection management
ash system is actually just a network between ashes."""

__author__ = "SeongJae Park"
__email__ = "sj38.park@gmail.com"
__copyright__ = "Copyright (c) 2011-2013, SeongJae Park"
__license__ = "GPLv3"

import socket
import threading

import ash

DEFAULT_PORT = 13131
_MAX_SOCKET_BUFFER_SIZE = 1024
DISCONN = "disconnected"
END_OF_MSG = 'end_of_expr'

_stop_accepting = False
_stop_listening = False

def start_daemon(port=DEFAULT_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', port))
    s.listen(1)

    _stop_listening = False
    _AcceptorThread(s).start()

def stop_daemon():
    _stop_accepting = True

def connectable_with(ip, port):
    try:
        s = connect(ip, port)
    except Exception, e:
        return False
    s.close()
    return True

# combine tokens received from socket, get complete message peer sent.
def get_complete_message(token, pre_tokens):
    """Get complete message seperated by END_OF_MSG"""
    pre_tokens += token
    complete_msgs = []
    while END_OF_MSG in pre_tokens:
        complete_msgs.append(pre_tokens[:pre_tokens.find(END_OF_MSG)])
        pre_tokens = pre_tokens[pre_tokens.find(END_OF_MSG) + len(END_OF_MSG):]
    return complete_msgs, pre_tokens

def connect(ip, port=DEFAULT_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.connect(ip, port)
    return sock

def send_expr(sock, expr):
    sock.sendall(expr + END_OF_MSG)
    tokens = ''
    while True:
        received = sock.recv(_MAX_SOCKET_BUFFER_SIZE)
        if not received:
            print "connection crashed!"
            sock.close()
            return (None, DISCONN)
        msgs, tokens = ashmon.get_complete_message(received, tokens)
        if len(msgs) <= 0:
            continue
        for msg in msgs:
            result = eval(msg)
            return (result, None)

class _AcceptorThread(threading.Thread):
    def __init__(self, sock):
        threading.Thread.__init__(self)
        self.sock = sock

    def run(self):
        while True:
            if _stop_accepting:
                global _stop_listening
                _stop_listening = True
                break
            conn, addr = self.sock.accept()
            print "connected by ash. start reader"
            reader = _ReaderThread(conn)
            reader.start()

class _ReaderThread(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        tokens = ''
        while True:
            if _stop_listening:
                break
            received = self.conn.recv(_MAX_SOCKET_BUFFER_SIZE)
            if not received:
                print "not received! stop listening!"
                break
            msgs, tokens = get_complete_message(received, tokens)
            for msg in msgs:
                result = ash.input(msg)
                self.conn.sendall("%s%s" % (result, END_OF_MSG))
        self.conn.close()
