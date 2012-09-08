import struct
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
Block = namedtuple("Block", ["piece_id", "player_id", "is_empty"])

class Piece(object):
	"""data is an ASCII representation of the piece"""
	def __init__(self, id, player_id, data):
		self.id = id
		self.player_id = player_id
		raise NotImplementedError()
		
	"""Gets a copy of this piece rotated clockwise by the specified number of steps"""
	def get_rotation(self, steps):
		raise NotImplementedError()
	
	"""Determines whether this piece is a valid rotation of the specified piece"""
	def is_rotation(self, piece):
		raise NotImplementedError()

"""The complete state of the game"""		
class Board(object):
	null_piece_id = 0xFFFF
	null_player_id = 0xFF

	"""Network order, Piece ID (ushort), Player ID (uchar)"""
	block_format = "!HB"
	null_block = struct.pack(data_format, 0xFFFF, 0xFF)
	
	def __init__(self, pieces, size, player_count):
		self.pieces = pieces
		self.size = size
		self.data = [[null_block] * size for x in xrange(size)]
	
	def get_block(self, position):
		assert position.x < size and position.y < size

		data = struct.unpack(data_format, self.data[position.x][position.y]))
		return Block(data[0], data[1], data[0] == null_piece_id)
	
	def place_piece(self, position, piece):
		def set_block(data, position, piece_id, player_id):
			raise NotImplementedError()
			
		raise NotImplementedError()
		
	def get_remaining_pieces(self, player_id):
		raise NotImplementedError()