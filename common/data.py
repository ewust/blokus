# vim: ts=4 et sw=4 sts=4

import math
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

class Piece(object):
    _cos_table = [ 1, 0, -1, 0 ]
    _sin_table = [ 0, 1, 0, -1 ]

    """
    size = the length of the longest axis of the piece
    coords = a list of coordinates that this piece occupies
    """
    def __init__(self, id, size, coords):
        self.id = id
        self.coords = coords
        self.size = size
        half_size = math.floor(size / 2)
        if size % 2 == 0:
            half_size += 1
        self.center = Point(half_size, half_size)
        
        for coord in coords:
            assert coord.x < size and coord.y < size
    
    """Constructs a Piece object from an ascii art representation of the desired shape"""
    @staticmethod
    def from_string(id, string):
        string = string.strip()
        max_x = 0
        max_y = string.count("\n")
        x = 0
        y = max_y
        coords = []
        for i in range(len(string)):
            if string[i] == ".":
                x += 1
            elif string[i] == "\n":
                if x > max_x:
                    max_x = x
            
                x = 0
                y -= 1
            else:
                coords.append(Point(x, y))
                x += 1
        
        return Piece(id, max(max_x, max_y), coords)
    
    def __repr__(self):
        def create_line(size):
            line = ["." for i in range(size)]
            line.append("\n")
            return line
        
        grid = [create_line(self.size) for i in range(self.size)]
        for coord in self.coords:
            grid[self.size - coord.y - 1][coord.x] = "O"
        
        grid_string = "".join(["".join(line) for line in grid])
        
        return "".join(["id=", str(self.id), "\n", grid_string])
    
    def equals(self, piece):
        if self.id != piece.id:
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
            for c in normalized_coords ]
        
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
        
class Board(object):
    """Network order (big-endian), Piece ID (ushort), Player ID (uchar)"""
    _block_format = "!HB"
    
    def __init__(self, pieces=None, size=DEFAULT_BOARD_SIZE, player_count=DEFAULT_PLAYER_COUNT):
        if (pieces):
            self.pieces = pieces
        else:
            # Default set of pieces
            raise NotImplementedError, "Default pieces"
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
    
    def get_remaining_pieces(self, player_id):
        raise NotImplementedError()
    
    def is_valid_move(self, move):
        raise NotImplementedError()
    
    def apply_move(self, move):
        for coord in move.piece.coords:
            x = coord.x + move.position.x
            y = coord.y + move.position.y
            self.set_block(move.position, move.piece_id, move.player_id)
