"""Abstract AI Bot class to be overridden by players"""
class Bot(object):
	def init(self, board):
		raise NotImplementedError()
	
	def get_move(self):
		raise NotImplementedError()
	
	def report_move(self, position, piece):
		raise NotImplementedError()
	
	def report_status(self, status_code, message):
		raise NotImplementedError()
		
