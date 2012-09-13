# vim: ts=4 et sw=4 sts=4

"""Abstract AI Bot class to be overridden by players"""
class Bot(object):
    STATUS_SKIPPED = 1      # Your turn was skipped, message explains why
    STATUS_GAME_OVER = 2    # This game has ended

    """Initializes the bot for a new game. Subclasses *must* call
    super(SubclassBot, self).__init__(player_id, board)"""
    def __init__(self, player_id, board):
        self.board = board
        self.player_id = player_id
        super(Bot, self).__init__()

    """Must return a Move object"""
    def get_move(self):
        raise NotImplementedError, "Abstract base class"

    """Reports every move made to this bot"""
    def report_move(self, move):
        assert not hasattr(super(Bot), 'report_move')

    """Reports a status message from the server to this bot
       (e.g. 'You took too long! Your turn has been skipped.')"""
    def report_status(self, status_code, message):
        assert not hasattr(super(Bot), 'report_status')

class SimpleStatusHandler(Bot):
    def report_status(self, status_code, message):
        if status_code is self.STATUS_SKIPPED:
            print "My turn was skipped: " + message
        else:
            raise NotImplementedError, "Unknown status: " +\
                    str(status_code) + ": " + message

        super(SimpleStatusHandler, self).report_status(status_code, message)

class PlayOnReport(Bot):
    """Bots which define their own report_move *must* call
    super(NewBotClass, self).report_move(move)"""
    def report_move(self, move):
        self.board.play_move(move)
        super(PlayOnReport, self).report_move(move)

class CornerLoggingBot(PlayOnReport):
    def __init__(self, **kwds):
        self.corner_set = set()
        super(CornerLoggingBot, self).__init__(**kwds)

    """Bots which define their own report_move should call
    super(NewBotClass, self).report_move(move)"""
    def report_move(self, move):
        super(CornerLoggingBot, self).report_move(move)
