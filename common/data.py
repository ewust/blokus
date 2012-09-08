from collections import namedtuple
from struct import pack, unpack

Point = namedtuple("Point", ["x", "y"])
Block = namedtuple("Block", ["piece_id", "player_id", "is_empty"])
Move = namedtuple("Move", ["position", "piece"])

class Piece(object):
	"""coords is a list of coordinates that this piece occupies"""
	def __init__(self, id, coords):
		self.id = id
		self.coords = coords
	
	"""Constructs a Piece object from an ascii art representation of the desired shape"""
	def from_string(string):
		raise NotImplementedError()
	
	"""Gets a copy of this piece rotated clockwise by the specified number of steps"""
	def get_rotation(self, steps):
		raise NotImplementedError()
	
	"""Determines whether this piece is a valid rotation of the specified piece"""
	def is_rotation(self, piece):
		raise NotImplementedError()
		
class Board(object):
	null_piece_id = 0xFFFF
	null_player_id = 0xFF

	"""Network order (big-endian), Piece ID (ushort), Player ID (uchar)"""
	block_format = "!HB"
	null_block = pack(block_format, 0xFFFF, 0xFF)
	
	def __init__(self, pieces, size, player_count):
		self.pieces = pieces
		self.size = size
		self.data = [[null_block] * size for x in xrange(size)]
	
	def get_block(self, position):
		assert position.x < size and position.y < size
		data = unpack(block_format, self.data[position.x][position.y]))
		return Block(data[0], data[1], data[0] == null_piece_id)
	
	def get_piece(self, piece_id):
		assert piece_id < len(self.pieces)
		return self.pieces[piece_id]
	
	def place_piece(self, position, piece, player_id):
		for coord in piece.coords:
			x = coord.x + position.x
			y = coord.y + position.y
			self.data[x][y] = pack(block_format, piece_id, player_id)
		
	def get_remaining_pieces(self, player_id):
		raise NotImplementedError()