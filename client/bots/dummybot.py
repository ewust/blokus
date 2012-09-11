# vim: ts=4 et sw=4 sts=4

from copy import copy

from common.data import Move
from common.data import Point
from common.bot import Bot

"""Dumbest bot that can play the game"""
class DummyBot(Bot):
    """Initializes the bot for a new game"""
    def __init__(self, player_id, board):
        self.board = board
        self.player_id = player_id
        self.remaining_pieces = copy(board.piece_factory.piece_ids)

    """Must return a Move object"""
    def get_move(self):
        for piece in self.remaining_pieces:
            for rotation in xrange(4):
                for x in xrange(self.board.size):
                    for y in xrange(self.board.size):
                        move = Move(self.player_id, piece, rotation, (x,y))
                        if self.board.is_valid_move(move):
                            self.remaining_pieces.remove(piece)
                            return move
        return Move.skip(self.player_id)

    """Reports every move made to this bot"""
    def report_move(self, move):
        self.board.play_move(move)

    """Reports a status message from the server to this bot
       (e.g. 'You took too long! Your turn has been skipped.')"""
    def report_status(self, status_code, message):
        if status_code is self.STATUS_SKIPPED:
            print "My turn was skipped: " + message
        else:
            raise NotImplementedError, "Unknown status: " +\
                    str(status_code) + ": " + message
