# vim: ts=4 et sw=4 sts=4

import math
import string
import unittest

from collections import namedtuple
from copy import deepcopy
from struct import pack, unpack

EMPTY_PIECE_ID = 0xFFFF
EMPTY_PLAYER_ID = 0xFF

DEFAULT_BOARD_SIZE = 20
DEFAULT_PLAYER_COUNT = 4

Point = namedtuple("Point", ["x", "y"])
Move = namedtuple("Move", ["position", "piece", "player_id"])
_Block = namedtuple("Block", ["piece_id", "player_id", "is_empty"])

def Block(piece_id, player_id):
    return _Block(piece_id, player_id, piece_id == EMPTY_PIECE_ID or player_id == EMPTY_PLAYER_ID)

"""
A piece represented as a set of coordinates.  No optimization here, just the
most generic representation of a piece that allows for the rules to be changed.
Make assumptions in your bots if you want a different representation.
"""
class Piece(object):
    _cos_table = [1, 0, -1, 0]
    _sin_table = [0, 1, 0, -1]

    """
    size = the length of the longest axis of the piece
    coords = a list of coordinates that this piece occupies
    """
    def __init__(self, piece_id, size, coords):
        self.piece_id = piece_id
        self.coords = coords
        self.size = size
        half_size = math.floor(size / 2)
        if size % 2 == 0:
            half_size += 1
        self.center = Point(half_size, half_size)
        
        for coord in coords:
            assert coord.x < size and coord.y < size
    
    """
    Constructs a Piece object from an ascii art representation of the desired
    shape. For example:
        ...O
        ...O
        ...O
        OOOO
        
    Dots represent a blank space and non-whitespace characters represent
    filled blocks.  The '\n' character is used to delimit rows and calculate
    the height of the Piece.
    """
    @staticmethod
    def from_string(piece_id, s):
        s = s.strip()
        max_x = 0
        max_y = s.count("\n")
        x = 0
        y = max_y
        coords = []
        for i in range(len(s)):
            if s[i] == ".":
                x += 1
            elif s[i] == "\n":
                if x > max_x:
                    max_x = x
            
                x = 0
                y -= 1
            elif s[i] in string.whitespace:
                pass
            else:
                coords.append(Point(x, y))
                x += 1
        
        return Piece(piece_id, max(max_x, max_y), coords)

    @staticmethod
    def from_repr(s):
        s = s.strip()
        piece_id, piece = s.split('\n', 1)
        piece_id = int(piece_id[3:])
        return self.from_string(piece_id, piece)

    @staticmethod
    def default_pieces():
        pieces_text = [
"""
.O.
.OO
OO.
""",
"""
.O.
.O.
OO.
""",
"""
OO.
.O.
OO.
""",
"""
.O.
.O.
OOO
""",
]
        pieces = []
        for i in range(len(pieces_text)):
            pieces.append(Piece.from_string(i, pieces_text[i]))
        return pieces

    def __repr__(self):
        def create_line(size):
            line = ["." for i in range(size)]
            line.append("\n")
            return line
        
        grid = [create_line(self.size) for i in range(self.size)]
        for coord in self.coords:
            grid[self.size - coord.y - 1][coord.x] = "O"
        
        grid_string = "".join(["".join(line) for line in grid])
        
        return "".join(["id=", str(self.piece_id), "\n", grid_string])
    
    def equals(self, piece):
        if self.piece_id != piece.piece_id:
            return False
            
        for coord in piece.coords:
            if not coord in self.coords:
                return False
                
        return True
        
    """Gets a copy of this piece rotated counter-clockwise by the specified number of steps"""
    def get_rotation(self, steps):
        assert steps >= 0
        
        rotation = deepcopy(self)
        
        steps = steps % 4
        if steps == 0:
            return rotation
        
        normalized_coords = [ Point(c.x - self.center.x, c.y - self.center.y) for c in self.coords ]
        
        cos = Piece._cos_table[steps]
        sin = Piece._sin_table[steps]
        rotation.coords = [ 
            Point(c.x * cos - c.y * sin + self.center.x,
                  c.x * sin + c.y * cos + self.center.y)
            for c in normalized_coords]
        
        return rotation
    
    """Gets the number of steps the given piece was rotated by to arrive at this piece"""
    def get_rotation_steps(self, piece):
        rotations = [self.get_rotation(i) for i in range(4)]
        for i in range(4):
            if rotations[i].equals(piece):
                return i
                
        raise ValueError("piece is not a valid rotation of this piece")
        
    """Determines whether this piece is a valid rotation of the specified piece"""
    def is_rotation(self, piece):
        rotations = [self.get_rotation(r) for r in range(4)]
        
        for rotation in rotations:
            if rotation.equals(piece):
                return True
                
        return False

"""
The full game state.  Note that this is written avoiding any assumptions about
how bots will use the data.  In other words, we give you interfaces to access
the board block-by-block, to access pieces associated with those blocks, and
to get information about per player pieces, but there are no optimizations.
The Board class holds the minimum state required to fully represent the game
and the helper functions are provided for convenience only.  More efficient
algorithms are the server and bots' responsibility.

For example, the server might subclass Board and implement caching of
remaining pieces of each player for efficiency.
"""
class Board(object):
    """Network order (big-endian), Piece ID (ushort), Player ID (uchar)"""
    _block_format = "!HB"
    
    def __init__(self, pieces=None, size=DEFAULT_BOARD_SIZE, player_count=DEFAULT_PLAYER_COUNT):
        if (pieces):
            self.pieces = set(pieces)
        else:
            # Default set of pieces
            self.pieces = set(Piece.default_pieces())
        self.size = size
        self.player_count = player_count
        
        null_block = pack(Board._block_format, EMPTY_PIECE_ID, EMPTY_PLAYER_ID)
        self._data = [[null_block] * size for x in range(size)]
    
    def get_block(self, position):
        assert position.x < size and position.y < size
        block_data = unpack(Board._block_format, self._data[position.x][position.y])
        return Block(block_data[0], block_data[1])
    
    def set_block(self, position, piece_id, player_id):
        assert position.x < size and position.y < size
        self._data[x][y] = pack(Board._block_format, move.piece_id, move.player_id)
    
    def get_piece(self, piece_id):
        assert piece_id < len(self.pieces)
        return self.pieces[piece_id]
    
    def get_used_pieces(self, player_id):
        used_pieces = set()
        for x in range(self.size):
            for y in range(self.size):
                block = self.get_block(Point(x, y))
                if block.player_id == player_id and not block.piece_id in used_pieces:
                    used_pieces.add(block.piece_id)
                    
        return used_pieces
    
    def get_remaining_pieces(self, player_id):
        return self.pieces - get_used_pieces(player_id)

    def is_valid_move(self, move):
        if move.piece_id >= len(self.pieces):
            return False
        
        if not move.piece_id in get_remaining_pieces(move.player_id):
            return False
        
        for coord in move.piece.coords:
            block = self.get_block(coord)
            if not block.is_empty:
                return False
                
        return True
    
    def is_valid_first_move(self, move):
        raise NotImplementedError()
    
    def apply_move(self, move):
        for coord in move.piece.coords:
            x = coord.x + move.position.x
            y = coord.y + move.position.y
            self.set_block(move.position, move.piece_id, move.player_id)
