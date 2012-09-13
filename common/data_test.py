# vim: ts=4 et sw=4 sts=4

import unittest

from common.data import *

class PieceTests(unittest.TestCase):
    def test_create_from_string(self):
        text = """
.O.
.XX
XX.
"""
        piece = Piece(piece_id=0, from_str=text)
        self.assertEqual(piece.coords,[(0,0),(0,1),(1,1),(-1,2),(0,2)])

    def test_create_from_normalized_coords(self):
        coords = [(0,0),(0,1),(1,1),(-1,2),(0,2)]
        piece = Piece(piece_id=0, from_coords=coords)
        self.assertEqual(piece.coords, coords)

    def test_create_from_non_normalized_coords(self):
        coords = [(1,2),(1,1),(2,1),(0,0),(1,0)]
        norm_coords = [(0,0),(0,1),(1,1),(-1,2),(0,2)]
        piece = Piece(piece_id=0, from_coords=coords)
        self.assertEqual(piece.coords, norm_coords)

    def test_to_string(self):
        piece = Piece(0, from_coords=[(0,0),(0,1),(-1,2),(0,2)])
        self.assertEqual(str(piece).strip(),
"""
id=0,size=3
.O
.X
XX
""".strip())

    def test_rotation(self):
        piece = Piece(0, 'OX.\n.X.\n.XX')
        self.assertEqual(piece.get_CCW_coords(0), [(0,0),(1,0),(1,1),(1,2),(2,2)])
        self.assertEqual(piece.get_CCW_coords(1), [(0,0),(0,1),(-1,1),(-2,1),(-2,2)])
        self.assertEqual(piece.get_CCW_coords(2), [(0,0),(-1,0),(-1,-1),(-1,-2),(-2,-2)])
        self.assertEqual(piece.get_CCW_coords(3), [(0,0),(0,-1),(1,-1),(2,-1),(2,-2)])
        self.assertEqual(piece.get_CCW_coords(0), [(0,0),(1,0),(1,1),(1,2),(2,2)])
        self.assertEqual(piece.get_CCW_coords(1), [(0,0),(0,1),(-1,1),(-2,1),(-2,2)])
        self.assertEqual(piece.get_CCW_coords(2), [(0,0),(-1,0),(-1,-1),(-1,-2),(-2,-2)])
        self.assertEqual(piece.get_CCW_coords(3), [(0,0),(0,-1),(1,-1),(2,-1),(2,-2)])
        self.assertEqual(piece.get_CCW_coords(4), [(0,0),(1,0),(1,1),(1,2),(2,2)])
        self.assertEqual(piece.get_CCW_coords(4), [(0,0),(1,0),(1,1),(1,2),(2,2)])

class BoardTests(unittest.TestCase):
    pass
