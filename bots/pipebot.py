from common import *

"""Pipes game events between the server and bots implemented outside of the
   python client application using stdio"""
class PipeBot(Bot):
    """Initializes the bot for a new game"""
    def init(self, player_id, board):
        raise NotImplementedError()
    
    """Must return a Move object"""
    def get_move(self):
        raise NotImplementedError()
    
    """Reports a move made by another player to this bot"""
    def report_move(self, move):
        raise NotImplementedError()
    
    """Reports a status message from the server to this bot
       (e.g. 'You took too long! Your turn has been skipped.')"""
    def report_status(self, status_code, message):
        raise NotImplementedError()