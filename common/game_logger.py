# vim: ts=4 et sw=4 sts=4

from common.data import PieceLibrary,Move

class GameLogger(object):
    def __init__(self, board, play=True, display=False, db=None):
        self.board = board
        self.play = play
        self.display = display

        self.o = open('game.log', 'w')
        self.o.write('#Version=0.11\n')
        self.o.write('#num_players=%d,rows=%d,cols=%d,library=%s\n' % (
            board.player_count,
            board.rows,
            board.cols,
            board.piece_library.library,
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

        self.o.flush()

class GameParser(object):
    def __init__(self, logfile):
        self.l = open(logfile)
        version = self.l.readline().strip().strip('#')
        txt,num = version.split('=')
        if txt.lower() != 'version':
            raise TypeError, "Unknown log file format. Line: " + version
        if float(num) > 0.11:
            raise TypeError, "Unknown log file format. Version: " + num

        try:
            params = self.l.readline().strip().strip('#')
            for param in params.split(','):
                name,val = param.split('=')
                if name.lower() == 'num_players':
                    self.num_players = int(val)
                elif name.lower() == 'size':
                    self.shape = (int(val), int(val))
                elif name.lower() == 'rows':
                    self.rows = int(val)
                elif name.lower() == 'cols':
                    self.cols = int(val)
                elif name.lower() == 'library':
                    self.library = val
                else:
                    print "Warn: Unknown param " + param
        except Exception as e:
            print params
            raise e

        try:
            if self.shape[0] != self.rows:
                raise TypeError, "Board Size Mismatch"
            self.rows = self.shape[0]
        except AttributeError:
            pass

        try:
            if self.shape[1] != self.cols:
                raise TypeError, "Board Size Mismatch"
            self.cols = self.shape[1]
        except AttributeError:
            pass

        self.shape = (self.rows, self.cols)

    def __iter__(self):
        return self

    def next(self):
        try:
            player_id, piece_id, rotation, x, y = self.l.readline().strip().split(',')
        except ValueError:
            raise StopIteration
        return Move(int(player_id), int(piece_id), int(rotation), (int(x),int(y)))
