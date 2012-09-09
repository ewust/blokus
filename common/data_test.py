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
    def get_test_rotations(self):
        pieces_text = [
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
        return [Piece.from_string(0, text) for text in pieces_text]
        
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
        piece = Piece(0, 3, [Point(0, 0), Point(1, 0), Point(1, 1), Point(1, 2)])
        self.assertEqual(str(piece).strip(),
"""
id=0
.O.
.O.
OO.
""".strip())
    
    def test_get_rotation(self):
        rotations = self.get_test_rotations()
        original = rotations[0]
        for step in range(4):
            self.assertTrue(rotations[step].equals(original.get_rotation(step)))
        
    def test_get_rotation_steps(self):
        rotations = self.get_test_rotations()
        original = rotations[0]
        for i in range(4):
            self.assertEqual(original.get_rotation_steps(rotations[i]), i)
        
    def test_is_rotation(self):
        rotations = self.get_test_rotations()
        original = rotations[0]
        for rotation in rotations:
            self.assertTrue(original.is_rotation(rotation))
            self.assertTrue(rotation.is_rotation(original))  
        
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
        