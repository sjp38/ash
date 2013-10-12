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

ASH_CONN_PORT = 13131

_stop_accepting = False
_stop_listening = False

def start_daemon():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('', ASH_CONN_PORT))
    s.listen(1)

    _stop_listening = False
    listener = _AcceptorThread(s)
    listener.start()

def stop_daemon():
    _stop_accepting = True

class _AcceptorThread(threading.Thread):
    def __init__(self, sock):
        self.sock = sock

    def run(self):
        while True:
            if _stop_accepting:
                global _stop_listening
                _stop_listening = True
                break
            conn, addr = self.sock.accept()
            print "connected by ash. start listener"
            listener = _ListenerThread(conn)
            listener.start()

_MAX_SOCKET_BUFFER_SIZE = 1024
END_OF_MSG = 'end_of_expr'

# combine tokens received from socket, get complete message peer sent.
def get_complete_message(token, pre_tokens):
    pre_tokens += token
    complete_msgs = []
    while END_OF_MSG in pre_tokens:
        complete_msgs.append(pre_tokens[:pre_tokens.find(END_OF_MSG)])
        pre_tokens = pre_tokens[pre_tokens.find(END_OF_MSG) + len(END_OF_MSG):]
    return complete_msgs, pre_tokens

class _ListenerThread(threading.Thread):
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.conn = conn

    def run(self):
        tokens = ''
        while True:
            if _stop_listening:
                break
            received = self.conn.recv(1024)
            if not received:
                print "not received! stop listening!"
                break
            msgs, tokens = get_complete_message(received, tokens)
            for msg in msgs:
                result = ash.input(msg)
                self.conn.sendall("%s%s" % (result, END_OF_MSG))
        self.conn.close()
