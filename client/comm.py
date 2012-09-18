# vim: ts=4 et sw=4 sts=4

from common.communication import Message
from common.data import Board,PieceLibrary
# temp, I don't like this much cross-ref..
from common.bot import Bot

class GameServer(object):

    def __init__(self, connection):
        self.connection = connection

    """Connects to server"""
    def join_game(self, board_constructor=None):
        self.sock = self.connection.get_socket()

        # Send join message, blocks until a new game is ready
        Message.serialized(self.sock, Message.TYPE_CONTROL, 'JOIN')

        m = Message(self.sock, Message.TYPE_ID)
        player_id = m.message_object

        m = Message(self.sock, Message.TYPE_BOARD, board_constructor)
        board = m.message_object

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
                raise NotImplementedError, "Unknown control message " + str(m)
        elif m.message_type is Message.TYPE_MOVE:
            bot.report_move(m.message_object)
        elif m.message_type is Message.TYPE_STATUS:
            if m.message_object[0] == Bot.STATUS_GAME_OVER:
                return False
            bot.report_status(m.message_object[0], m.message_object[1])
        else:
            raise NotImplementedError, "Unknown message type " + str(m)
        return True
