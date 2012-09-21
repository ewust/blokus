# vim: ts=4 et sw=4 sts=4

import os
import math
import string
import unittest
import struct

EMPTY_PIECE_ID = 0xFFFF
EMPTY_PLAYER_ID = 0xFF

DEFAULT_BOARD_SHAPE = (20,20)
DEFAULT_PLAYER_COUNT = 4

class Move(object):
    SKIP=-1
    ILLEGAL=-2
    TIMEOUT=-3

    move_id = 0

    def __init__(self,
            player_id,
            piece_id,
            rotation=0,
            mirror=False,
            position=(0,0),
            ):
        self.player_id = player_id
        self.piece_id = piece_id
        self.rotation = rotation
        self.mirror = mirror
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

    def is_voluntary_skip(self):
        return self.piece_id == Move.SKIP

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
            return "Player %d played piece %d rotated %d degrees%s at %s" % (
                    self.player_id,
                    self.piece_id,
                    self.rotation*90,
                    ["", " (mirrored)"][self.mirror],
                    str(self.position)
                    )

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
A piece represented as a set of coordinates. Some helpful utility functions
are included here. Most are memoized.
"""
class Piece(object):
    _cos_table = [1, 0, -1, 0]
    _sin_table = [0, 1, 0, -1]

    CORNER_COORDS = ((-1, -1), (-1, 1), (1, 1), (1, -1))
    EDGE_COORDS = ((-1, 0), (1, 0), (0, -1), (0, 1))

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
            self.coords = [Point(c[0],c[1]) for c in from_coords]
        else:
            raise TypeError, "Piece constructor requires a builder (str, coords)"
        self.normalize_coords()

        self.rot = {}
        self.edges = {}
        self.corners = {}

    def _gen_repr_keys(self):
        return "piece_id=%d, from_coords=%s," % (self.piece_id, str(self.coords))

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self._gen_repr_keys())

    def __str__(self):
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

        return "id=%d,size=%d\n%s" % (self.piece_id, self.shape[1], grid)

    def verbose(self):
        grid = ""
        for y in xrange(self.min_y-1, self.max_y+1+1):
            for x in xrange(self.min_x-1, self.max_x+1+1):
                if (x, y) in self.coords:
                    if (x,y) == self.coords[0]:
                        grid += 'O'
                    else:
                        grid += 'X'
                elif (x, y) in self.get_edges():
                    grid += 'e'
                elif (x, y) in self.get_corners():
                    grid += 'c'
                else:
                    grid += '.'
            grid += '\n'

        return "id=%d,size=%d\n%s" % (self.piece_id, self.shape[1], grid)


    def __eq__(self, piece):
        return self.piece_id == piece.piece_id

    def __ne__(self, piece):
        return self.piece_id != piece.piece_id

    def __hash__(self):
        return hash(self.piece_id)

    def __len__(self):
        return len(self.coords)

    def __getitem__(self, key):
        return self.coords[key]

    def __contains__(self, point):
        return point in self.coords

    def __iter__(self):
        self._next = -1
        return self

    def next(self):
        self._next += 1
        try:
            return self.coords[self._next]
        except IndexError:
            raise StopIteration

    """Returns the coordinates of this piece rotated counter-clockwise nsteps"""
    def get_transform_coords(self, rotation=0, mirror=False):
        rotation %= 4

        try:
            return self.rot[(rotation,mirror)]
        except KeyError:
            rcoords = [Point(c.x, c.y) for c in self.coords]

            n = rotation
            while n:
                n -= 1
                for c in rcoords:
                    (c.x, c.y) = (-c.y, c.x)

            if mirror:
                for c in rcoords:
                    c.x = -c.x

            self.rot[(rotation,mirror)] = rcoords
            return rcoords

    """Returns the edges of this piece, optionally transformed"""
    def get_edges(self, rotation=0, mirror=False):
        rotation %= 4

        try:
            return self.edges[(rotation,mirror)]
        except KeyError:
            edges = set()

            for pt in self.get_transform_coords(rotation=rotation,mirror=mirror):
                for e in Piece.EDGE_COORDS:
                    t = pt + e
                    if t not in self.coords:
                        edges.add(t)

            self.edges[(rotation,mirror)] = list(edges)
            return self.edges[(rotation,mirror)]

    """Returns the corners of this piece, optionally transformed"""
    def get_corners(self, rotation=0, mirror=False):
        rotation %= 4

        try:
            return self.corners[(rotation,mirror)]
        except KeyError:
            corners = set()

            for pt in self.get_transform_coords(rotation=rotation,mirror=mirror):
                for c in Piece.CORNER_COORDS:
                    t = pt + c
                    if t not in self.coords and t not in self.get_edges(rotation=rotation,mirror=mirror):
                        corners.add(t)

            self.corners[(rotation,mirror)] = list(corners)
            return self.corners[(rotation,mirror)]

class PieceLibrary(object):
    PieceClass = Piece
    PieceClassKwds = {}

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

            self.pieces[pc_id] = self.PieceClass(piece_id=pc_id, from_str=pc, **self.PieceClassKwds)

        self.piece_ids = set(self.pieces.keys())
        self.used_piece_ids = set()

    def __getitem__(self, pc_id):
        return self.pieces[pc_id]

    def __iter__(self):
        self._next = -1
        return self

    def next(self):
        self._next += 1
        try:
            return self.__getitem__(self._next)
        except KeyError:
            raise StopIteration

    def play_move(self, move):
        if not move.is_skip():
            self.used_piece_ids.add(move.piece_id)

    def unplay_move(self, move):
        if not move.is_skip():
            self.used_piece_ids.remove(move.piece_id)

    def get_used_piece_ids(self):
        return self.used_piece_ids

    def get_remaining_piece_ids(self):
        return self.piece_ids - self.used_piece_ids


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


class Board(object):
    BlockClass = Block
    BlockClassKwds = {}

    """
    Base exception class for this object
    """
    class BoardError(Exception):
        pass

    class IllegalMove(BoardError):
        pass

    def build_board(self):
        self.board = [
                [self.BlockClass(**self.BlockClassKwds) for x in xrange(self.rows)]
                      for y in xrange(self.cols)]

        # Hacky :/
        self._back_refs = {}
        for y in xrange(self.cols):
            for x in xrange(self.rows):
                self._back_refs[self.board[x][y]] = Point(x,y)

    def build_piece_libraries(self):
        self.piece_library = {x : PieceLibrary(
            self.library,
            self.restrict_piece_ids_to,
            ) for x in xrange(self.player_count)}

    """A Board object:

    library               -- A string describing a known piece library
    restrict_piece_ids_to -- OPTIONAL: Limit the pieces from the library to this set
    shape                 -- A (rows,cols) tuple describing the board dimensions
    player_count          -- The number of players
    """
    def __init__(self,
            library,
            restrict_piece_ids_to=None,
            shape=DEFAULT_BOARD_SHAPE,
            player_count=DEFAULT_PLAYER_COUNT,
            ):
        self.library = library
        self.restrict_piece_ids_to = restrict_piece_ids_to
        self.shape = shape
        self.rows = shape[0]
        self.cols = shape[1]
        self.corners = (
                Point(0,0),
                Point(0,self.cols-1),
                Point(self.rows-1, 0),
                Point(self.rows-1, self.cols-1),
                )
        self.player_count = player_count

        self.build_piece_libraries()
        self.build_board()

        self.moves = [list() for x in xrange(player_count)]
        self.turn = 0
        self.skips = [False for x in xrange(player_count)]

    def valid_key(self, key):
        if key.x not in xrange(self.rows) or key.y not in xrange(self.cols):
            raise IndexError

    def __getitem__(self, key):
        key = Point(key)
        self.valid_key(key)
        return self.board[key.x][key.y]

    def __setitem__(self, key, val):
        key = Point(key)
        self.valid_key(key)
        if isinstance(val, self.BlockClass):
            self.board[key.x][key.y] = val
        else:
            raise TypeError, str(self.BlockClass) + " expected"

    def index(self, elem):
        return self._back_refs[elem]

    def get_piece(self, piece_id):
        return self.piece_library[piece_id]

    def get_used_piece_ids(self, player_id):
        return self.piece_library[player_id].get_used_piece_ids()

    def get_remaining_piece_ids(self, player_id):
        return self.piece_library[player_id].get_remaining_piece_ids()

    def is_valid_move(self, move, first_move=False, ignore_turn=False):
        if not first_move and len(self.moves[move.player_id]) == 0:
            return self.is_valid_first_move(move)

        self._valid_reason = "XXX Unset XXX"

        if move.is_skip():
            self._valid_reason = "Skip Succeeded"
            return True

        if move.player_id != self.turn:
            self._valid_reason = "Current turn %d, move id %d" % (
                    self.turn, move.player_id)
            return False

        if not move.piece_id in self.get_remaining_piece_ids(move.player_id):
            self._valid_reason = "Piece %d not in %d's remaining pieces" % (
                    move.piece_id, move.player_id)
            return False

        coords = self.move_coords(move)

        # Flag set if we're touching ourselves, pre-set for first move
        corner_touch = first_move

        for coord in coords:
            try:
                if self[coord].move:
                    self._valid_reason = \
"Cannot play in coord %s, which has move %s" % (str(coord), str(self[coord].move))
                    return False
            except IndexError:
                self._valid_reason =\
"Illegal coord %s is outside board area" % (str(coord))
                return False

            # Check for edge touches of this block [illegal]
            for neigh in Piece.EDGE_COORDS:
                try:
                    if self[coord + neigh].move.player_id == move.player_id:
                        self._valid_reason = \
"Cannot play in coord %s, neighbors %s with move %s" % (
        str(coord), str(coord + neigh), self[coord + neigh].move)
                        return False
                except (IndexError, AttributeError):
                    pass

            if not corner_touch:
                # Check for a corner touch [required]
                for neigh in Piece.CORNER_COORDS:
                    try:
                        if self[coord + neigh].move.player_id == move.player_id:
                            corner_touch = True
                            break
                    except (IndexError, AttributeError):
                        pass

        if not corner_touch:
            self._valid_reason = "Move touches no corners"
        return corner_touch

    def move_coords(self, move):
        piece = self.piece_library[move.player_id][move.piece_id]
        rot = piece.get_transform_coords(rotation=move.rotation, mirror=move.mirror)
        coords = [coord + move.position for coord in rot]
        return coords

    def do_move(self, move, unplay=False):
        if not unplay:
            self.moves[move.player_id].append(move)

            if move.is_voluntary_skip():
                self.skips[self.turn] = True

            if all(self.skips):
                self.turn = -1
            else:
                self.turn = (self.turn + 1) % self.player_count
                while self.skips[self.turn]:
                    self.turn = (self.turn + 1) % self.player_count
        else:
            if move != self.moves[move.player_id][-1]:
                raise KeyError, "Moves must be unplayed in reverse chrono order"
            self.moves[move.player_id].pop(-1)

            # Safe as unplayed move is known to be last move from above
            self.turn = move.player_id

            if move.is_voluntary_skip():
                self.skips[self.turn] = False

        if move.is_skip():
            return

        if not unplay:
            self.piece_library[move.player_id].play_move(move)
        else:
            self.piece_library[move.player_id].unplay_move(move)

        for coord in self.move_coords(move):
            if not unplay:
                self[coord].move = move
            else:
                self[coord].move = None

    def play_move(self, move):
        self.do_move(move)

    def unplay_move(self, move):
        self.do_move(move, True)

    """
    On the first move, players are only allowed to place pieces that touch
    corners of the board. This returns whether the specified move is valid as
    a first move for any given player.  A move is valid if the piece is valid
    and it touches a corner
    """
    def is_valid_first_move(self, move):
        if not self.is_valid_move(move, True):
            return False

        for coord in self.move_coords(move):
            if coord in self.corners:
                return True

        self._valid_reason = "First move must be in a corner"

        return False
