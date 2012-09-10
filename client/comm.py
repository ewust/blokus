# vim: ts=4 et sw=4 sts=4

from common.communication import Message

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

        while True:
            m = Message(self.sock)
            if m.message_type != Message.TYPE_CONTROL:
                raise TypeError, "Expected CONTROL message in response to JOIN"

            if m.message_object == 'START':
                break
            elif m.message_object == 'WAIT':
                print "Got WAIT"
                continue
            else:
                raise NotImplementedError, "Unknown CONTROL message " + str(m)

    """Blocking "event" loop - waits for the server to send us messages"""
    def game_loop(self):
        m = Message(self.sock)
        if m.message_type is Message.TYPE_CONTROL:
            if m.message_object == 'TURN':
                Message.serialized(self.sock, Message.TYPE_MOVE, bot.get_move())
            elif m.message_object == 'END':
                return False
            else:
                raise NotImplementedError, "Unknown CONTROL message " + str(m)
        elif m.message_type is Message.TYPE_MOVE:
            bot.report_move(m.message_object)
        else:
            raise NotImplementedError, "Unknown message type " + str(m)
        return True