# vim: ts=4 et sw=4 sts=4

from copy import copy
from common.data import Move

"""Abstract AI Bot class to be overridden by players"""
class Bot(object):
    STATUS_SKIPPED = 1      # Your turn was skipped, message explains why
    STATUS_GAME_OVER = 2    # This game has ended

    """Initializes the bot for a new game. Subclasses *must* be of the form

    def __init__(self, [args_to_consume,...], **kwds):

    and *must* **first** call

    super(SubclassBot, self).__init__(**kwds)"""
    def __init__(self, player_id, board, **kwds):
        super(Bot, self).__init__(**kwds)
        self.board = board
        self.player_id = player_id

    """Must return a Move object"""
    def get_move(self):
        assert not hasattr(super(Bot), 'get_move')
        return Move.skip(self.player_id)

    """Reports every move made to this bot"""
    def report_move(self, move):
        assert not hasattr(super(Bot), 'report_move')

    """Reports a status message from the server to this bot
       (e.g. 'You took too long! Your turn has been skipped.')"""
    def report_status(self, status_code, message):
        assert not hasattr(super(Bot), 'report_status')

## REPORT_MOVE EXTENDERS ##

class PieceTracker(Bot):
    def __init__(self, **kwds):
        super(PieceTracker, self).__init__(**kwds)
        self.remaining_pieces = copy(self.board.piece_library.piece_ids)

    def report_move(self, move):
        if not move.is_skip() and move.player_id == self.player_id:
            self.remaining_pieces.remove(move.piece_id)
        super(PieceTracker, self).report_move(move)

class PlayOnReport(Bot):
    """Bots which define their own report_move *must* call
    super(NewBotClass, self).report_move(move)"""
    def report_move(self, move):
        self.board.play_move(move)
        super(PlayOnReport, self).report_move(move)

class CornerLogger(PlayOnReport):
    def __init__(self, **kwds):
        super(CornerLoggingBot, self).__init__(**kwds)
        self.corner_set = set()

    """Bots which define their own report_move should call
    super(NewBotClass, self).report_move(move)"""
    def report_move(self, move):
        if not move.is_skip():
            if move.player_id == self.player_id:
                for c in self.board.move_coords(move):
                    for neigh in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
                        pot = c + neigh
                        try:
                            if self.board[pot].move is None:
                                self.corner_set.add(pot)
                        except (IndexError):
                            pass

            for c in self.board.move_coords(move):
                try:
                    self.corner_set.remove(c)
                except KeyError:
                    pass

        super(CornerLoggingBot, self).report_move(move)

## GET_MOVE EXTENDERS ##

class ExhaustiveSearchBot(PieceTracker,PlayOnReport):
    def get_move(self):
        for piece in self.remaining_pieces:
            for rotation in xrange(4):
                for x in xrange(self.board.cols):
                    for y in xrange(self.board.rows):
                        move = Move(self.player_id, piece, rotation, (x,y))
                        if self.board.is_valid_move(move):
                            return move

        return super(ExhaustiveSearchBot, self).get_move()

## REPORT_STATUS EXTENDERS ##

class SimpleStatusHandler(Bot):
    def report_status(self, status_code, message):
        if status_code is self.STATUS_SKIPPED:
            print "My turn was skipped: " + message
        else:
            raise NotImplementedError, "Unknown status: " +\
                    str(status_code) + ": " + message

        super(SimpleStatusHandler, self).report_status(status_code, message)
