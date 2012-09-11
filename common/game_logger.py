# vim: ts=4 et sw=4 sts=4

from common.data import PieceFactory,Move

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

class GameParser(object):
    def __init__(self, logfile):
        self.l = open(logfile)
        version = self.l.readline().strip().strip('#')
        txt,num = version.split('=')
        if txt.lower() != 'version':
            raise TypeError, "Unknown log file format. Line: " + version
        if float(num) != 0.1:
            raise TypeError, "Unknown log file format. Version: " + num

        params = self.l.readline().strip().strip('#')
        for param in params.split(','):
            name,val = param.split('=')
            if name.lower() == 'num_players':
                self.num_players = int(val)
            elif name.lower() == 'size':
                self.size = int(val)
            elif name.lower() == 'library':
                self.library = val
            else:
                print "Warn: Unknown param " + param

        self.piece_factory = PieceFactory(self.library)

    def __iter__(self):
        return self

    def next(self):
        try:
            player_id, piece_id, rotation, x, y = self.l.readline().strip().split(',')
        except ValueError:
            raise StopIteration
        return Move(int(player_id), int(piece_id), int(rotation), (int(x),int(y)))
