# vim: ts=4 et sw=4 sts=4

import sys

from common.gui import BlockusGui
from common.game_logger import GameParser

class ReplayGui(BlockusGui):
    pass

if __name__ == '__main__':
    try:
        game = GameParser(sys.argv[1])
    except IndexError as e:
        print "USAGE:"
        print sys.argv[0] + ' game.log'
        sys.exit(1)
    b = BlockusGui(game.size, game.size, game.piece_factory)
    for move in game:
        b.add_move(move)
    b.main()
