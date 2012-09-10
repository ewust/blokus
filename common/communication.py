# vim: ts=4 et sw=4 sts=4

import socket
import json
import struct

from common.data import Board

class BlockusEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Board):
            r = []
            r.append(obj.size)
            r.append(obj.player_count)
            r.append(len(obj.pieces))
            for p in obj.pieces:
                r.append(repr(p))
            return r
        return json.JSONEncoder.default(self, obj)

class Message():
    TYPE_CONTROL = 1
    TYPE_BOARD = 2
    TYPE_MOVE = 3

    @staticmethod
    def serialized(sock, message_type, message_object):
        msg = json.dumps((message_type, message_object), cls=BlockusEncoder)
        l = struct.pack(">I", len(msg))
        sock.send(l)
        sock.send(msg)

    """Takes a socket and blocks until it has read exactly enough
    bytes to parse out one message"""
    def __init__(self, sock, message_type=None):
        i = sock.recv(4, socket.MSG_WAITALL)
        i = struct.unpack(">I", i)[0]

        msg = sock.recv(i, socket.MSG_WAITALL)
        self.message_type, self.message_object = json.loads(msg)

        if message_type and message_type != self.message_type:
            raise TypeError, "Bad Message Type"

    def match(self, message_type, message_object):
        if self.message_type != message_type:
            return False
        if self.message_object != message_object:
            return False
        return True
