# vim: ts=4 et sw=4 sts=4

import socket
import errno
import json
import struct

from common.data import Board,Move,PieceLibrary,Point

class BlockusEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Board):
            r = []
            r.append(obj.library)
            r.append(obj.restrict_piece_ids_to)
            r.append(obj.shape)
            r.append(obj.player_count)
            return r
        elif isinstance(obj, Move):
            return [
                    obj.player_id,
                    obj.piece_id,
                    obj.rotation,
                    obj.mirror,
                    obj.position
                    ]
        elif isinstance(obj, Point):
            return [obj.x, obj.y]
        return json.JSONEncoder.default(self, obj)

class Message():
    TYPE_CONTROL = 0
    TYPE_STATUS = 1
    TYPE_ID = 2
    TYPE_BOARD = 3
    TYPE_MOVE = 4

    @staticmethod
    def serialized(sock, message_type, message_object, suppress_err=None):
        msg = json.dumps((message_type, message_object), cls=BlockusEncoder)
        l = struct.pack(">I", len(msg))

        if suppress_err is None:
            suppress_err = message_type == Message.TYPE_STATUS

        try:
            sock.send(l)
            sock.send(msg)
        except socket.error as e:
            if e.errno != errno.EPIPE:
                print "Unexpected error: ", e
            if not suppress_err:
                raise e

    def printer(self, rep):
        s = ""
        if self.message_type is Message.TYPE_CONTROL:
            s += "CONTROL: "
            s += str(self.message_object)
        elif self.message_type is Message.TYPE_STATUS:
            s += "STATUS: "
            s += str(self.message_object)
        elif self.message_type is Message.TYPE_BOARD:
            s += "\nBOARD: "
            s += "\tsize: " + str(self.message_object[0])
            s += "\tplayer_count: " + str(self.message_object[1])
            s += "\tnum_pieces: " + str(self.message_object[2])
            if (rep):
                for p in self.message_object[3:]:
                    s += str(p)
        elif self.message_type is Message.TYPE_MOVE:
            s += "MOVE: "
            s += str(self.message_object)
        else:
            s += "\n\nUNKNOWN? [This is an error]\n"
            s += "Type: " + str(self.message_type)
            s += "Object: " + str(self.message_object)
        return s

    def __str__(self):
        return self.printer(False)

    def __repr__(self):
        return self.printer(True)

    """Takes a socket and blocks until it has read exactly enough
    bytes to parse out one message"""
    def __init__(self, sock, message_type=None, object_constructor=None):
        i = sock.recv(4, socket.MSG_WAITALL)
        if len(i) == 0:
            raise IOError, "Socket Closed"
        i = struct.unpack(">I", i)[0]

        msg = sock.recv(i, socket.MSG_WAITALL)
        self.message_type, self.message_object = json.loads(msg)

        if message_type and message_type != self.message_type:
            raise TypeError, "Bad Message Type"

        if self.message_type == Message.TYPE_BOARD:
            if object_constructor is None:
                object_constructor = Board
            self.message_object = object_constructor(
                    library=self.message_object[0],
                    restrict_piece_ids_to=self.message_object[1],
                    shape=self.message_object[2],
                    player_count=self.message_object[3],
                    )
        elif self.message_type == Message.TYPE_MOVE:
            if object_constructor is None:
                object_constructor = Move
            self.message_object = object_constructor(
                    player_id=self.message_object[0],
                    piece_id=self.message_object[1],
                    rotation=self.message_object[2],
                    mirror=self.message_object[3],
                    position=self.message_object[4],
                    )

    def match(self, message_type, message_object):
        if self.message_type != message_type:
            return False
        if self.message_object != message_object:
            return False
        return True
