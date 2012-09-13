# vim: ts=4 et sw=4 sts=4

import os
import math
import string
import unittest
import struct

EMPTY_PIECE_ID = 0xFFFF
EMPTY_PLAYER_ID = 0xFF

DEFAULT_BOARD_SIZE = 20
DEFAULT_PLAYER_COUNT = 4

class Move(object):
    SKIP=-1
    ILLEGAL=-2
    TIMEOUT=-3

    move_id = 0

    def __init__(self, player_id, piece_id, rotation=0, position=(0,0)):
        self.player_id = player_id
        self.piece_id = piece_id
        self.rotation = rotation
        self.position = Point(position)

        self.move_id = Move.move_id
        Move.move_id += 1

    @staticmethod
    def skip(player_id):
        return Move(player_id, Move.SKIP)

    @staticmethod
    def illegal(player_id):
        return Move(player_id, Move.ILLEGAL)

    @staticmethod
    def timeout(player_id):
        return Move(player_id, Move.TIMEOUT)

    def is_skip(self):
        return self.piece_id < 0

    def __str__(self):
        if self.piece_id == Move.SKIP:
            return "Player %d skipped their turn" % (self.player_id)
        elif self.piece_id == Move.ILLEGAL:
            return "Player %d made an illegal move and their turn was skipped" %\
                    (self.player_id)
        elif self.piece_id == Move.TIMEOUT:
            return "Player %d timed out and their turn was skipped" %\
                    (self.player_id)
        else:
            return "Player %d played piece %d rotated %d degrees at %s" %\
                    (self.player_id, self.piece_id, self.rotation*90, str(self.position))

    def __repr__(self):
        return "Move #" + str(self.move_id) + ": " + str(self)

class Point(object):
    def __init__(self, coords, coords_as_two_args=None):
        if coords_as_two_args is not None:
            self.x = coords
            self.y = coords_as_two_args
        else:
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
                    raise TypeError, "Two roots in piece string:\n" + s
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
                x = self.coords[c].x - root.x
                y = root.y - self.coords[c].y
                self.coords[c] = Point(x,y)

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
        if piece_id < 0:
            raise TypeError, "Piece IDs must be >= 0"
        self.piece_id = piece_id

        if from_str:
            self.coords = self.coords_from_str(from_str)
        elif from_coords:
            self.coords = list(from_coords)
        else:
            raise TypeError, "Piece constructor requires a builder (str, coords)"
        self.normalize_coords()

        self.rot = {}

    def __repr__(self):
        grid = ""
        for y in xrange(self.min_y, self.max_y+1):
            for x in xrange(self.min_x, self.max_x+1):
                if (x, y) in self.coords:
                    if (x,y) == self.coords[0]:
                        grid += 'O'
                    else:
                        grid += 'X'
                else:
                    grid += '.'
            grid += '\n'

        return "%s\nid=%d,size=%d\n%s" % (str(self.coords), self.piece_id, self.shape[1], grid)

    def equals(self, piece):
        return self.piece_id == piece.piece_id

    """Returns the coordinates of this piece rotated counter-clockwise nsteps"""
    def get_CCW_coords(self, nsteps=1):
        assert nsteps >= 0

        try:
            raise KeyError
            return self.rot[nsteps]
        except KeyError:
            rcoords = list(self.coords)

            n = nsteps
            while n:
                n -= 1
                rcoords = [Point(-c.y, c.x) for c in rcoords]

            self.rot[nsteps] = rcoords
            return rcoords

class PieceFactory(object):
    def __init__(self, library, restrict_piece_ids_to=None):
        self.library = library
        self.pieces = {}

        l = None
        for f in (
                library,\
                os.path.join('resources',library),\
                os.path.join('resources','pieces',library),\
                os.path.join('common','resources','pieces',library),\
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

            if restrict_piece_ids_to and pc_id not in restrict_piece_ids_to:
                continue

            self.pieces[pc_id] = Piece(pc_id, from_str=pc)

        self.piece_ids = set(self.pieces.keys())

    def __getitem__(self, pc_id):
        return self.pieces[pc_id]


class Block(object):
    """Network order (big-endian), Piece ID (ushort), Player ID (uchar)"""
    block_format = "!HB"
    max_block = 0

    def __init__(self, move=None):
        self.move = move

        self.block_id = Block.max_block
        Block.max_block += 1

    def pack(self):
        return struct.pack(Block.block_format, self.piece_id, self.player_id)

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

    """
    Base exception class for this object
    """
    class BoardError(Exception):
        pass

    class IllegalMove(BoardError):
        pass

    def __init__(self, piece_factory, size=DEFAULT_BOARD_SIZE, player_count=DEFAULT_PLAYER_COUNT):
        if isinstance(piece_factory, str):
            self.piece_factory = PieceFactory(piece_factory)
        elif isinstance(piece_factory, PieceFactory):
            self.piece_factory = piece_factory
        else:
            raise TypeError, "Bad piece_factory"

        self.size = size
        self.player_count = player_count

        self.board = [[Block() for x in xrange(size)] for y in xrange(size)]
        self.moves = [list() for x in xrange(player_count)]

    def valid_key(self, key):
        if key.x not in xrange(self.size) or key.y not in xrange(self.size):
            raise IndexError

    def __getitem__(self, key):
        key = Point(key)
        self.valid_key(key)
        return self.board[key.x][key.y]

    def __setitem__(self, key, val):
        key = Point(key)
        self.valid_key(key)
        if isinstance(val, Block):
            self.board[key.x][key.y] = val
        else:
            raise TypeError, "Block object required"

    def get_piece(self, piece_id):
        return self.piece_factory[piece_id]

    def get_used_piece_ids(self, player_id):
        used_pieces = set()
        for x in range(self.size):
            for y in range(self.size):
                block = self[(x, y)]
                if block.move and block.move.player_id == player_id:
                    used_pieces.add(block.move.piece_id)

        return used_pieces

    def get_remaining_piece_ids(self, player_id):
        return self.piece_factory.piece_ids - self.get_used_piece_ids(player_id)

    def is_valid_piece(self, piece_id):
        return piece_id in self.piece_factory.piece_ids

    def is_valid_move(self, move, first_move=False):
        if not first_move and len(self.moves[move.player_id]) == 0:
            return self.is_valid_first_move(move)

        if move.is_skip():
            return True

        if not move.piece_id in self.get_remaining_piece_ids(move.player_id):
            return False

        coords = self.move_coords(move)

        # Flag set if we're touching ourselves, pre-set for first move
        corner_touch = first_move

        for coord in coords:
            try:
                if self[coord].move:
                    return False
            except IndexError:
                return False

            # Check for edge touches of this block [illegal]
            for neigh in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                try:
                    if self[coord + neigh].move.player_id == move.player_id:
                        return False
                except (IndexError, AttributeError):
                    pass

            if not corner_touch:
                # Check for a corner touch [required]
                for neigh in ((-1, -1), (-1, 1), (1, 1), (1, -1)):
                    try:
                        if self[coord + neigh].move.player_id == move.player_id:
                            corner_touch = True
                            break
                    except (IndexError, AttributeError):
                        pass

        return corner_touch

    def move_coords(self, move):
        piece = self.piece_factory[move.piece_id]
        rot = piece.get_CCW_coords(move.rotation)
        coords = [coord + move.position for coord in rot]
        return coords

    def play_move(self, move):
        self.moves[move.player_id].append(move)

        if move.is_skip():
            return

        piece = self.piece_factory[move.piece_id]
        coords = piece.get_CCW_coords(move.rotation)

        for coord in coords:
            self[move.position + coord].move = move


    """
    On the first move, players are only allowed to place pieces that touch
    corners of the board. This returns whether the specified move is valid as
    a first move for any given player.  A move is valid if the piece is valid
    and it touches a corner
    """
    def is_valid_first_move(self, move):
        if not self.is_valid_piece(move.piece_id):
            return False

        if not self.is_valid_move(move, True):
            return False

        max_value = self.size - 1
        for coord in self.piece_factory[move.piece_id].get_CCW_coords(move.rotation):
            coord += move.position
            if ((coord.x == 0 and coord.y == 0) or
                (coord.x == 0 and coord.y == max_value) or
                (coord.x == max_value and coord.y == max_value) or
                (coord.x == max_value and coord.y == 0)):
                return True

        return False
