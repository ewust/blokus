import unittest

from common.data import *
        
class BlockTests(unittest.TestCase):
    def test_create(self):
        block = Block(0, 0)
        self.assertEqual(block.piece_id, 0)
        self.assertEqual(block.player_id, 0)
        self.assertFalse(block.is_empty)
    
    def test_empty(self):
        block = Block(EMPTY_PIECE_ID, 0)
        self.assertTrue(block.is_empty)
        block = Block(0, EMPTY_PLAYER_ID)
        self.assertTrue(block.is_empty)
        
class PieceTests(unittest.TestCase):
    def test_create(self):
        pass
        
    def test_create_from_string(self):
        text = """
.O.
.OO
OO.
"""

        piece = Piece.from_string(0, text)
        self.assertEqual(str(piece).strip(),
"""
id=0
.O.
.OO
OO.
""".strip())
    
    def test_to_string(self):
        piece = Piece(0, [ Point(0, 0), Point(1, 0), Point(1, 1), Point(1, 2) ])
        self.assertEqual(str(piece).strip(),
"""
id=0
.O
.O
OO
""".strip())
    
    def test_get_rotation(self):
        pass
        
    def test_get_rotation_steps(self):
        pass
        
    def test_is_rotation(self):
        pass
        
class BoardTests(unittest.TestCase):
    _pieces_text = [
        """
        .O.
        OOO
        ...
        """,
        """
        .O.
        OO.
        .O.
        """,
        """
        ...
        OOO
        .O.
        """,
        """
        .O.
        .OO
        .O.
        """ ]

    def test_block_data(self):
        pass
        