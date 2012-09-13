# vim: ts=4 et sw=4 sts=4

from copy import copy

from common.data import Move
from common.data import Point
from common.bot import SimpleStatusHandler,CornerLoggingBot

"""Dumbest bot that can play the game"""
class DummyBot(SimpleStatusHandler, CornerLoggingBot):
    """Initializes the bot for a new game"""
    def __init__(self, **kwds):
        super(DummyBot, self).__init__(**kwds)

        self.remaining_pieces = copy(self.board.piece_factory.piece_ids)
        self.have_skipped = False

    """Must return a Move object"""
    def get_move(self):
        if self.have_skipped:
            return Move.skip(self.player_id)

        for piece in self.remaining_pieces:
            for rotation in xrange(4):
                for x in xrange(self.board.size):
                    for y in xrange(self.board.size):
                        move = Move(self.player_id, piece, rotation, (x,y))
                        if self.board.is_valid_move(move):
                            self.remaining_pieces.remove(piece)
                            return move

        self.have_skipped = True
        return Move.skip(self.player_id)
