# vim: ts=4 et sw=4 sts=4

from common.communication import Message
from common.data import Board,Piece

#from SSL_client import SSL_Connection as Connection
from Clear_client import Clear_Connection as Connection

class ServerConnection(object):

    def __init__(self, server=None):
        self.server = server

    """Connects to server"""
    def join_game(self):
        self.conn = Connection()
        self.conn.connect()
        self.sock = self.conn.get_socket()

        # Send join message, blocks until a new game is ready
        Message.serialized(self.sock, Message.TYPE_CONTROL, 'JOIN')

        m = Message(self.sock, Message.TYPE_ID)
        player_id = m.message_object

        m = Message(self.sock, Message.TYPE_BOARD)
        size = m.message_object.pop(0)
        player_count = m.message_object.pop(0)
        num_pieces = m.message_object.pop(0)
        pieces = []
        for p in m.message_object:
            pieces.append(Piece.from_repr(p))
        board = Board(size=size, player_count=player_count,pieces=pieces)

        m = Message(self.sock, Message.TYPE_CONTROL)
        if m.message_object != 'WAIT':
            raise NotImplementedError, "Unknown CONTROL message " + str(m)

        return player_id, board

    """Blocking "event" loop - waits for the server to send us messages"""
    def game_loop(self, bot):
        m = Message(self.sock)
        if m.message_type is Message.TYPE_CONTROL:
            if m.message_object == 'TURN':
                Message.serialized(self.sock, Message.TYPE_MOVE, bot.get_move())
            elif m.message_object == 'END':
                return False
            else:
                print "==========================="
                print m
                print m.message_object
                print "==========================="
                raise NotImplementedError, "Unknown control message " + str(m)
        elif m.message_type is Message.TYPE_MOVE:
            bot.report_move(m.message_object)
        else:
            raise NotImplementedError, "Unknown message type " + str(m)
        return True
