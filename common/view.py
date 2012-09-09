"""Abstract view of a game of Blokus"""
class View(object):
    def init(self, player_id, board):
        raise NotImplementedError()

    def report_move(self, move):
        raise NotImplementedError()

    def report_status(self, status_code, message):
        raise NotImplementedError()
