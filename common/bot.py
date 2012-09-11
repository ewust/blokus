﻿# vim: ts=4 et sw=4 sts=4

"""Abstract AI Bot class to be overridden by players"""
class Bot(object):
    STATUS_SKIPPED = 1      # Your turn was skipped, message explains why
    STATUS_GAME_OVER = 2    # This game has ended

    """Initializes the bot for a new game"""
    def init(self, player_id, board):
        raise NotImplementedError()
    
    """Must return a Move object"""
    def get_move(self):
        raise NotImplementedError()
    
    """Reports every move made to this bot"""
    def report_move(self, move):
        raise NotImplementedError()
    
    """Reports a status message from the server to this bot
       (e.g. 'You took too long! Your turn has been skipped.')"""
    def report_status(self, status_code, message):
        raise NotImplementedError()
