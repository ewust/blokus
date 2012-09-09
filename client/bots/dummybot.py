from common import *
from copy import copy

"""Dumbest bot that can play the game"""
class DummyBot(Bot):
    """Initializes the bot for a new game"""
    def init(self, player_id, board):
        self.board = board
        self.player_id = player_id
        self.remaining_pieces = copy(board.pieces)
    
    """Must return a Move object"""
    def get_move(self):
        for piece in self.remaining_pieces:
            for rotation in [piece.get_rotation(i) for i in range(4)]:
                for x in xrange(self.board.size):
                    for y in xrange(self.board.size):
                        move = Move(Point(x, y), rotation, self.player_id)
                        if self.board.is_valid_move(move):
                            return move
    
    """Reports a move made by another player to this bot"""
    def report_move(self, move):
        self.board.apply_move(move)
    
    """Reports a status message from the server to this bot
       (e.g. 'You took too long! Your turn has been skipped.')"""
    def report_status(self, status_code, message):
        pass
