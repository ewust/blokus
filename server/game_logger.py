# vim: ts=4 et sw=4 sts=4

class GameLogger(object):
    def __init__(self, board, play=True, display=False, db=None):
        self.board = board
        self.play = play
        self.display = display

        self.o = open('game.log', 'w')
        self.o.write('#Version=0.1\n')
        self.o.write('#num_players=%d,size=%d,library=%s\n' % (
            board.player_count,
            board.size,
            board.piece_factory.library,
            ))

    def add_move(self, move):
        if self.display:
            print repr(move)

        if self.play:
            self.board.play_move(move)

        self.o.write("%d,%d,%d,%d,%d\n" % (
            move.player_id,
            move.piece_id,
            move.rotation,
            move.position.x,
            move.position.y,
            ))
