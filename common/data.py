# vim: ts=4 et sw=4 sts=4

import os
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

Move = namedtuple("Move", ["position", "piece", "player_id"])
_Block = namedtuple("Block", ["piece_id", "player_id", "is_empty"])

def Block(piece_id, player_id):
    return _Block(piece_id, player_id, piece_id == EMPTY_PIECE_ID or player_id == EMPTY_PLAYER_ID)


class Point(object):
    def __init__(self, coords):
        self.x = coords[0]
        self.y = coords[1]

    def __repr__(self):
        return "(%d, %d)" % (self.x, self.y)

    def __neg__(self):
        return Point((-self.x, -self.y))

    def __add__(self, other):
        return Point((self.x + other[0], self.y + other[1]))

    def __sub__(self, other):
        return self + -other

    def __eq__(self, other):
        return (self.x == other[0]) and (self.y == other[1])

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.x, self.y))

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError

    def __setitem__(self, key, v):
        if key == 0:
            self.x = v
        elif key == 1:
            self.y = v
        else:
            raise IndexError

"""
A piece represented as a set of coordinates.  No optimization here, just the
most generic representation of a piece that allows for the rules to be changed.
Make assumptions in your bots if you want a different representation.
"""
class Piece(object):
    _cos_table = [1, 0, -1, 0]
    _sin_table = [0, 1, 0, -1]

    """
    Constructs a Piece object from an ascii art representation of the desired
    shape. For example:
        OXXX
        X..X
        X...
        X...

    Dots represent a blank space, 'X' and 'O' characters represent filled
    blocks.  The '\n' character is used to delimit rows and calculate the height
    of the Piece.  The special character 'O' represents the 'root' of the piece.
    A piece is rotated around its root, and built from the root when placed.
    """
    def coords_from_str(self, s):
        found_root = False

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
            elif s[i] == 'O':
                if found_root:
                    raise TypeError, "Two roots in piece string"
                found_root = True
                coords.insert(0, Point((x,y)))
                x += 1
            else:
                coords.append(Point((x, y)))
                x += 1

        if not found_root:
            raise TypeError, "No root in piece string"

        return coords


    """
    Internal - Pieces are stored with the root coordinate at (0,0) so adjust
    the coordinates if need be. Also compute the piece's shape
    """
    def normalize_coords(self):
        root = self.coords[0]
        if root != (0,0):
            for c in xrange(len(self.coords)):
                self.coords[c] = Point(self.coords[c] - root)

        self.coords = self.coords

        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0
        for x,y in self.coords:
            self.min_x = min(x, self.min_x)
            self.min_y = min(y, self.min_y)
            self.max_x = max(x, self.max_x)
            self.max_y = max(y, self.max_y)

        self.shape = (self.max_x - self.min_x + 1, self.max_y - self.min_y + 1)

    """
    piece_id    - The unique id assigned to this piece from its piece library
    from_str    - A valid 'piece_str' (see above) to construct this piece from
    from_coords - The set of coordinates this piece occupies, **root first**
    """
    def __init__(self, piece_id, from_str=None, from_coords=None):
        self.piece_id = piece_id

        if from_str:
            self.coords = self.coords_from_str(from_str)
        elif from_coords:
            self.coords = list(from_coords)
        else:
            raise TypeError, "Piece constructor requires a builder (str, coords)"
        self.normalize_coords()

    def __repr__(self):
        print self.shape
        print self.coords
        print self.min_x
        print self.max_x
        print self.min_y
        print self.max_y
        grid = ""
        for y in xrange(self.max_y, self.min_y-1, -1):
            for x in xrange(self.min_x, self.max_x+1):
                if (x, y) in self.coords:
                    if (x,y) == self.coords[0]:
                        grid += 'O'
                    else:
                        grid += 'X'
                else:
                    grid += '.'
            grid += '\n'

        return "id=%d,size=%d\n%s" % (self.piece_id, self.shape[1], grid)

    def equals(self, piece):
        return self.piece_id == piece.piece_id

    """Returns the coordinates of this piece rotated counter-clockwise nsteps"""
    def get_CCW_coords(self, nsteps=1):
        assert nsteps >= 0

        rcoords = list(self.coords)

        while nsteps:
            nsteps -= 1
            rcoords = [Point(-c.y, c.x) for c in rcoords]

        return rcoords

class PieceFactory(object):
    def __init__(self, library):
        self.library = library
        self.pieces = {}

        l = None
        for f in (
                library,\
                os.path.join('resources',library),\
                os.path.join('resources','pieces',library),\
                ):
            try:
                l = open(f, 'r')
                break
            except IOError:
                pass
        if l is None:
            raise IOError, "Failed to find piece library"

        while True:
            meta = l.readline()
            if meta == '':
                break

            pc_id = None
            size = None
            for field in meta.split(','):
                name,val = field.split('=')
                if name == 'id':
                    pc_id = int(val)
                elif name == 'size':
                    size = int(val)
                else:
                    # Ignore unknown fields
                    # logger.debug(...)?
                    pass
            if (pc_id is None) or (size is None):
                continue

            pc = ""
            for x in xrange(size):
                pc += l.readline()

            self.pieces[pc_id] = Piece(pc_id, from_str=pc)

    def get(self, pc_id):
        return self.pieces[pc_id]


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
            self.pieces = pieces
        else:
            self.pieces = Board.get_default_pieces()
        
        # Initialize piece IDs so we can use list index as piece ID
        for i in range(len(self.pieces)):
            self.pieces[i].piece_id = i
        
        self.size = size
        self.player_count = player_count
        
        null_block = pack(Board._block_format, EMPTY_PIECE_ID, EMPTY_PLAYER_ID)
        self._data = [[null_block] * size for x in range(size)]
    
    def get_block(self, position):
        assert position.x < self.size and position.y < self.size
        block_data = unpack(Board._block_format, self._data[position.x][position.y])
        return Block(block_data[0], block_data[1])
    
    def set_block(self, position, piece_id, player_id):
        assert position.x < self.size and position.y < self.size
        self._data[position.x][position.y] = pack(Board._block_format, piece_id, player_id)
    
    def get_piece(self, piece_id):
        assert piece_id < len(self.pieces)
        return self.pieces[piece_id]
    
    def get_used_piece_ids(self, player_id):
        used_pieces = set()
        for x in range(self.size):
            for y in range(self.size):
                block = self.get_block(Point(x, y))
                if block.player_id == player_id and not block.piece_id in used_pieces:
                    used_pieces.add(block.piece_id)
                    
        return used_pieces
    
    def get_remaining_piece_ids(self, player_id):
        piece_ids = set([piece.piece_id for piece in self.pieces])
        return piece_ids - self.get_used_piece_ids(player_id)

    def is_valid_piece(self, piece):
        if piece.piece_id >= len(self.pieces):
            return False
        
        actual = self.pieces[piece.piece_id]
        return actual.is_rotation(piece)
        
    def is_valid_move(self, move):
        if not self.is_valid_piece(move.piece):
            return False
        
        if not move.piece.piece_id in self.get_remaining_piece_ids(move.player_id):
            return False
        
        for coord in move.piece.coords:
            block = self.get_block(coord)
            if not block.is_empty:
                return False
                
        return True
    
    """
    On the first move, players are only allowed to place pieces that touch
    corners of the board. This returns whether the specified move is valid as
    a first move for any given player.  A move is valid if the piece is valid
    and it touches a corner
    """
    def is_valid_first_move(self, move):
        if not self.is_valid_piece(move.piece):
            return False
        
        max_value = self.size - 1
        for coord in move.piece.coords:
            if ((coord.x == 0 and coord.y == 0) or
                (coord.x == 0 and coord.y == max_value) or
                (coord.x == max_value and coord.y == max_value) or
                (coord.x == max_value and coord.y == 0)):
                return True
                
        return False
    
    def apply_move(self, move):
        for coord in move.piece.coords:
            x = coord.x + move.position.x
            y = coord.y + move.position.y
            self.set_block(move.position, move.piece.piece_id, move.player_id)
            
    @staticmethod
    def get_default_pieces():
        pieces_text = [
"""
..O..
..O..
..O..
..O..
..O..
""",

"""
.O..
.O..
.O..
.O..
""",

"""
.O.
.O.
.O.
""",

"""
O.
O.
""",

"""
O
""",

"""
O..
O..
OOO
""",

"""
.O..
.O..
.O..
.OO.
""",

"""
.O.
.O.
.OO
""",

"""
O.
OO
""",

"""
OO
OO
""",

"""
.O.
.OO
.O.
""",

"""
.O..
.OO.
.O..
.O..
""",

"""
..O.
.OO.
.O..
.O..
""",

"""
..O
OOO
O..
""",

"""
.O
OO
O.
""",

"""
OO.
.OO
.O.
""",

"""
.O.
OOO
.O.
""",

"""
O..
OO.
.OO
""",

"""
.O.
.O.
OOO
""",

"""
O.O
OOO
...
""",

"""
.O.
OO.
OO.
"""]
        return [Piece.from_string(0, text) for text in pieces_text]
