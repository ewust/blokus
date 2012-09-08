"""Abstract AI Bot class to be overridden by players"""
class Bot(object):
	"""Initializes the bot for a new game"""
	def init(self, board):
		raise NotImplementedError()
	
	"""Must return a Move object"""
	def get_move(self):
		raise NotImplementedError()
	
	"""Reports a move made by another player to this bot"""
	def report_move(self, position, piece, player_id):
		raise NotImplementedError()
	
	"""Reports a status message from the server to this bot"""
	def report_status(self, status_code, message):
		raise NotImplementedError()
		
